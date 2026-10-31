        function initDriveAuth() {
            const hadRedirectToken = processDriveOAuthRedirect();
            const hasStoredToken = loadDriveTokenFromStorage();
            if (isInhouseApp) {
                updateDriveAuthUI();
                if (hadRedirectToken || hasStoredToken) {
                    refreshDriveFiles();
                } else if (useAndroidPkceFlow()) {
                    let hasRefresh = false;
                    try {
                        hasRefresh = localStorage.getItem(GOOGLE_SCOPE_VERSION_KEY) === GOOGLE_SCOPE_VERSION
                            && !!localStorage.getItem(DRIVE_REFRESH_TOKEN_KEY);
                    } catch (err) {}
                    if (hasRefresh) {
                        refreshDriveAccessTokenWithRefreshToken()
                            .then(() => refreshDriveFiles())
                            .catch(err => {
                                console.warn('Silent token refresh failed:', err);
                                updateDriveAuthUI();
                            });
                    }
                }
                return;
            }
            if (!window.google || !google.accounts || !google.accounts.oauth2) {
                setTimeout(initDriveAuth, 200);
                return;
            }
            driveTokenClient = google.accounts.oauth2.initTokenClient({
                client_id: GOOGLE_CLIENT_ID,
                scope: GOOGLE_API_SCOPE,
                include_granted_scopes: true,
                callback: () => { },
                error_callback: (err) => {
                    console.warn('Google popup auth failed:', err);
                }
            });
            updateDriveAuthUI();
            if (hadRedirectToken) {
                refreshDriveFiles();
            } else if (hasStoredToken) {
                refreshDriveFiles();
            } else if (localStorage.getItem(DRIVE_REMEMBER_KEY) === '1') {
                ensureDriveToken(false)
                    .then(() => refreshDriveFiles())
                    .catch(() => updateDriveAuthUI());
            }
        }

        function getDriveRedirectUri() {
            return `${window.location.origin}/?oauth_callback=1`;
        }

        function openAndroidAuthUrl(authUrl) {
            if (window.InhouseNative && typeof window.InhouseNative.openAuthUrl === 'function') {
                window.InhouseNative.openAuthUrl(authUrl);
                return true;
            }
            return false;
        }

        function generatePkceVerifier() {
            const bytes = new Uint8Array(32);
            crypto.getRandomValues(bytes);
            return base64UrlEncodeBytes(bytes);
        }

        function base64UrlEncodeBytes(bytes) {
            let bin = '';
            for (let i = 0; i < bytes.length; i++) bin += String.fromCharCode(bytes[i]);
            return btoa(bin).replace(/\+/g, '-').replace(/\//g, '_').replace(/=+$/, '');
        }

        async function pkceChallengeFromVerifier(verifier) {
            const data = new TextEncoder().encode(verifier);
            const digest = await crypto.subtle.digest('SHA-256', data);
            return base64UrlEncodeBytes(new Uint8Array(digest));
        }

        async function startAndroidPkceSignIn() {
            try {
                localStorage.setItem(DRIVE_REMEMBER_KEY, '1');
            } catch (err) {}
            const verifier = generatePkceVerifier();
            try { localStorage.setItem(DRIVE_PKCE_VERIFIER_KEY, verifier); } catch (err) {}
            const challenge = await pkceChallengeFromVerifier(verifier);
            const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
            authUrl.searchParams.set('client_id', ANDROID_OAUTH_CLIENT_ID);
            authUrl.searchParams.set('redirect_uri', ANDROID_PKCE_REDIRECT_URI);
            authUrl.searchParams.set('response_type', 'code');
            authUrl.searchParams.set('scope', GOOGLE_API_SCOPE);
            authUrl.searchParams.set('access_type', 'offline');
            authUrl.searchParams.set('include_granted_scopes', 'true');
            authUrl.searchParams.set('code_challenge', challenge);
            authUrl.searchParams.set('code_challenge_method', 'S256');
            authUrl.searchParams.set('state', 'inhouse_notes_pkce');
            try {
                const hint = localStorage.getItem('drive-hint-email');
                if (hint) authUrl.searchParams.set('login_hint', hint);
            } catch (err) {}
            const hasFreshConsent = (() => {
                try {
                    return localStorage.getItem('drive-consent-granted') === '1'
                        && localStorage.getItem(GOOGLE_SCOPE_VERSION_KEY) === GOOGLE_SCOPE_VERSION;
                }
                catch (e) { return false; }
            })();
            if (!hasFreshConsent) {
                authUrl.searchParams.set('prompt', 'consent');
            }
            const url = authUrl.toString();
            if (!openAndroidAuthUrl(url)) {
                console.warn('PKCE sign-in: Android bridge unavailable, falling back to web flow.');
                window.location.assign(url);
                return;
            }
            if (driveStatusEl) driveStatusEl.textContent = 'Complete sign-in in the Google window.';
        }

        async function exchangeAuthCodeForTokens(code) {
            let verifier = '';
            try { verifier = localStorage.getItem(DRIVE_PKCE_VERIFIER_KEY) || ''; } catch (err) {}
            if (!verifier) throw new Error('Missing PKCE verifier');
            const body = new URLSearchParams();
            body.set('client_id', ANDROID_OAUTH_CLIENT_ID);
            body.set('code', code);
            body.set('code_verifier', verifier);
            body.set('grant_type', 'authorization_code');
            body.set('redirect_uri', ANDROID_PKCE_REDIRECT_URI);
            const res = await fetch('https://oauth2.googleapis.com/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: body.toString()
            });
            if (!res.ok) {
                const text = await res.text().catch(() => '');
                throw new Error(`Token exchange failed: ${res.status} ${text}`);
            }
            const data = await res.json();
            try { localStorage.removeItem(DRIVE_PKCE_VERIFIER_KEY); } catch (err) {}
            applyTokenResponse(data, /*isRefresh*/ false);
            return data;
        }

        async function refreshDriveAccessTokenWithRefreshToken() {
            let refreshToken = '';
            try { refreshToken = localStorage.getItem(DRIVE_REFRESH_TOKEN_KEY) || ''; } catch (err) {}
            if (!refreshToken) throw new Error('No refresh token stored');
            if (!ANDROID_OAUTH_CLIENT_ID) throw new Error('Android OAuth client ID not configured');
            const body = new URLSearchParams();
            body.set('client_id', ANDROID_OAUTH_CLIENT_ID);
            body.set('grant_type', 'refresh_token');
            body.set('refresh_token', refreshToken);
            const res = await fetch('https://oauth2.googleapis.com/token', {
                method: 'POST',
                headers: { 'Content-Type': 'application/x-www-form-urlencoded' },
                body: body.toString()
            });
            if (!res.ok) {
                const text = await res.text().catch(() => '');
                if (res.status === 400 || res.status === 401) {
                    // Refresh token revoked or invalid — drop it so user re-auths.
                    try { localStorage.removeItem(DRIVE_REFRESH_TOKEN_KEY); } catch (err) {}
                }
                throw new Error(`Refresh failed: ${res.status} ${text}`);
            }
            const data = await res.json();
            applyTokenResponse(data, /*isRefresh*/ true);
            return driveAccessToken;
        }

        function applyTokenResponse(data, isRefresh) {
            if (!data || !data.access_token) throw new Error('Token response missing access_token');
            driveSignedOut = false;
            driveAuthNeedsReconnect = false;
            const expiresIn = parseInt(data.expires_in || '3600', 10);
            driveAccessToken = data.access_token;
            driveTokenExpiry = Date.now() + Math.max(60, expiresIn) * 1000;
            const grantedScopes = normalizeGrantedScopes(data.scope);
            if (!hasGoogleScope(grantedScopes, CALENDAR_SCOPE)) {
                driveAccessToken = null;
                driveTokenExpiry = 0;
                clearDriveTokenStorage();
                throw new Error('Calendar access was not granted by Google.');
            }
            saveDriveTokenToStorage(driveAccessToken, driveTokenExpiry, grantedScopes);
            if (data.refresh_token) {
                try { localStorage.setItem(DRIVE_REFRESH_TOKEN_KEY, data.refresh_token); } catch (err) {}
            }
            try { localStorage.setItem('drive-consent-granted', '1'); } catch (err) {}
            try { localStorage.setItem(GOOGLE_SCOPE_VERSION_KEY, GOOGLE_SCOPE_VERSION); } catch (err) {}
            scheduleDriveTokenRefresh();
            updateDriveAuthUI();
        }

        function startDriveRedirectSignIn() {
            if (useAndroidPkceFlow()) {
                startAndroidPkceSignIn().catch(err => {
                    console.error('PKCE sign-in failed:', err);
                    if (driveStatusEl) driveStatusEl.textContent = 'Sign-in failed. Try again.';
                });
                return;
            }
            try {
                localStorage.setItem(DRIVE_REMEMBER_KEY, '1');
            } catch (err) {}
            const authUrl = new URL('https://accounts.google.com/o/oauth2/v2/auth');
            authUrl.searchParams.set('client_id', GOOGLE_CLIENT_ID);
            authUrl.searchParams.set('redirect_uri', getDriveRedirectUri());
            authUrl.searchParams.set('response_type', 'token');
            authUrl.searchParams.set('scope', GOOGLE_API_SCOPE);
            authUrl.searchParams.set('include_granted_scopes', 'true');
            authUrl.searchParams.set('state', 'inhouse_notes_app');
            try {
                const hint = localStorage.getItem('drive-hint-email');
                if (hint) authUrl.searchParams.set('login_hint', hint);
            } catch (err) {}
            const hasFreshConsent = (() => {
                try {
                    return localStorage.getItem('drive-consent-granted') === '1'
                        && localStorage.getItem(GOOGLE_SCOPE_VERSION_KEY) === GOOGLE_SCOPE_VERSION;
                }
                catch (err) { return false; }
            })();
            if (!hasFreshConsent) {
                authUrl.searchParams.set('prompt', 'consent');
            }
            const url = authUrl.toString();
            if (isInhouseApp && openAndroidAuthUrl(url)) {
                if (driveStatusEl) driveStatusEl.textContent = 'Complete sign-in in the Google window.';
                return;
            }
            window.location.assign(url);
        }

        function completeDriveSignInFromParams(params) {
            const oauthError = params.get('error');
            if (oauthError) {
                if (oauthError && driveStatusEl) {
                    driveStatusEl.textContent = `Sign-in failed: ${oauthError}`;
                }
                return false;
            }
            const token = params.get('access_token');
            if (!token) return false;
            const grantedScopes = normalizeGrantedScopes(params.get('scope'));
            if (!hasGoogleScope(grantedScopes, CALENDAR_SCOPE)) {
                clearDriveTokenStorage();
                if (driveStatusEl) {
                    driveStatusEl.textContent = 'Calendar access was not granted. Sign in again and accept Calendar access.';
                }
                return false;
            }
            driveSignedOut = false;
            driveAuthNeedsReconnect = false;
            const expiresIn = parseInt(params.get('expires_in') || '3600', 10);
            driveAccessToken = token;
            driveTokenExpiry = Date.now() + Math.max(60, expiresIn) * 1000;
            saveDriveTokenToStorage(driveAccessToken, driveTokenExpiry, grantedScopes);
            try { localStorage.setItem('drive-consent-granted', '1'); } catch (err) {}
            try { localStorage.setItem(GOOGLE_SCOPE_VERSION_KEY, GOOGLE_SCOPE_VERSION); } catch (err) {}
            scheduleDriveTokenRefresh();
            updateDriveAuthUI();
            try {
                window.history.replaceState({}, document.title, window.location.pathname + window.location.search);
            } catch (err) {}
            return true;
        }

        function processDriveOAuthRedirect() {
            const rawHash = (window.location.hash || '').replace(/^#/, '');
            const rawSearch = (window.location.search || '').replace(/^\?/, '');
            if (!rawHash.includes('access_token=') && !rawHash.includes('error=') && !rawSearch.includes('error=')) {
                return false;
            }
            return completeDriveSignInFromParams(new URLSearchParams(rawHash || rawSearch));
        }

        function scheduleDriveTokenRefresh() {
            if (driveTokenRefreshTimer) clearTimeout(driveTokenRefreshTimer);
            driveTokenRefreshTimer = null;
            if (!driveAccessToken || !driveTokenExpiry) return;
            // Refresh 5 minutes before expiry
            const refreshIn = driveTokenExpiry - Date.now() - 5 * 60 * 1000;
            if (refreshIn <= 0) return;
            driveTokenRefreshTimer = setTimeout(() => {
                driveTokenRefreshTimer = null;
                // Silently refresh the token
                ensureDriveToken(false).catch(() => { });
            }, refreshIn);
        }

        function ensureDriveToken(interactive = false) {
            if (driveSignedOut && !interactive) {
                return Promise.reject(new Error('Signed out'));
            }
            if (interactive) {
                driveSignedOut = false;
                driveAuthNeedsReconnect = false;
            }
            if (driveAccessToken && Date.now() < driveTokenExpiry - 60000) {
                return Promise.resolve(driveAccessToken);
            }
            // Android PKCE path: silently refresh using stored refresh_token, no popup ever.
            if (useAndroidPkceFlow()) {
                let hasRefresh = false;
                try {
                    hasRefresh = localStorage.getItem(GOOGLE_SCOPE_VERSION_KEY) === GOOGLE_SCOPE_VERSION
                        && !!localStorage.getItem(DRIVE_REFRESH_TOKEN_KEY);
                } catch (err) {}
                if (hasRefresh) {
                    return refreshDriveAccessTokenWithRefreshToken().catch(err => {
                        if (!interactive) markDriveAuthNeedsReconnect(err?.message || 'refresh failed');
                        throw err;
                    });
                }
                if (interactive) {
                    startAndroidPkceSignIn().catch(() => { });
                }
                if (!interactive) markDriveAuthNeedsReconnect('missing refresh token');
                return Promise.reject(new Error('No refresh token; user must sign in'));
            }
            if (!driveTokenClient) {
                return Promise.reject(new Error('Drive auth not ready'));
            }
            return new Promise((resolve, reject) => {
                let settled = false;
                const timeoutId = setTimeout(() => {
                    if (settled) return;
                    settled = true;
                    const err = new Error('Silent token refresh timed out');
                    if (!interactive) markDriveAuthNeedsReconnect(err.message);
                    reject(err);
                }, interactive ? 60000 : 9000);
                driveTokenClient.callback = (resp) => {
                    if (settled) return;
                    settled = true;
                    clearTimeout(timeoutId);
                    if (resp.error) {
                        if (!interactive) markDriveAuthNeedsReconnect(resp.error);
                        reject(resp);
                        return;
                    }
                    driveAuthNeedsReconnect = false;
                    driveAccessToken = resp.access_token;
                    driveTokenExpiry = Date.now() + (resp.expires_in || 0) * 1000;
                    const grantedScopes = normalizeGrantedScopes(resp.scope);
                    if (!hasGoogleScope(grantedScopes, CALENDAR_SCOPE)) {
                        driveAccessToken = null;
                        driveTokenExpiry = 0;
                        reject(new Error('Calendar access was not granted by Google.'));
                        return;
                    }
                    saveDriveTokenToStorage(driveAccessToken, driveTokenExpiry, grantedScopes);
                    scheduleDriveTokenRefresh();
                    updateDriveAuthUI();
                    resolve(driveAccessToken);
                };
                const reqOptions = {};
                reqOptions.scope = GOOGLE_API_SCOPE;
                reqOptions.include_granted_scopes = true;
                if (interactive) {
                    reqOptions.prompt = 'consent';
                } else {
                    reqOptions.prompt = 'none'; // Bug fix: silent refresh, no popup
                    // Pass hint to auto-select the account without showing the picker
                    const email = driveUserProfile?.email || localStorage.getItem('drive-hint-email');
                    if (email) reqOptions.login_hint = email;
                }
                driveTokenClient.requestAccessToken(reqOptions);
            });
        }

        function signInDrive() {
            driveSignedOut = false;
            driveAuthNeedsReconnect = false;
            if (isInhouseApp) {
                startDriveRedirectSignIn();
                return;
            }
            ensureDriveToken(true)
                .then(() => refreshDriveFiles())
                .catch(() => {
                    if (driveStatusEl) driveStatusEl.textContent = 'Sign-in failed. Try again.';
                });
        }

        function saveDriveTokenToStorage(token, expiry, grantedScopes = GOOGLE_API_SCOPE) {
            try {
                const payload = JSON.stringify({ token, expiry, scopeVersion: GOOGLE_SCOPE_VERSION, grantedScopes });
                localStorage.setItem(DRIVE_TOKEN_KEY, payload);
                localStorage.setItem(DRIVE_REMEMBER_KEY, '1');
                localStorage.setItem(GOOGLE_SCOPE_VERSION_KEY, GOOGLE_SCOPE_VERSION);
                localStorage.setItem(GOOGLE_GRANTED_SCOPES_KEY, grantedScopes || '');
            } catch (e) {
                console.error('Failed to save Drive token:', e);
            }
        }

        function hasGoogleScope(scopeString, requiredScope) {
            return String(scopeString || '')
                .split(/\s+/)
                .filter(Boolean)
                .includes(requiredScope);
        }

        function normalizeGrantedScopes(scopeString) {
            return String(scopeString || GOOGLE_API_SCOPE);
        }

        function clearDriveTokenStorage() {
            try {
                localStorage.removeItem(DRIVE_TOKEN_KEY);
            } catch (e) {
                console.error('Failed to clear Drive token:', e);
            }
        }

        function loadDriveTokenFromStorage() {
            try {
                const raw = localStorage.getItem(DRIVE_TOKEN_KEY);
                if (!raw) return false;
                const parsed = JSON.parse(raw);
                if (!parsed || !parsed.token || !parsed.expiry) return false;
                if (parsed.scopeVersion !== GOOGLE_SCOPE_VERSION
                    || localStorage.getItem(GOOGLE_SCOPE_VERSION_KEY) !== GOOGLE_SCOPE_VERSION) {
                    clearDriveTokenStorage();
                    return false;
                }
                const grantedScopes = parsed.grantedScopes || localStorage.getItem(GOOGLE_GRANTED_SCOPES_KEY) || '';
                if (!hasGoogleScope(grantedScopes, CALENDAR_SCOPE)) {
                    clearDriveTokenStorage();
                    return false;
                }
                if (Date.now() >= parsed.expiry - 60000) {
                    clearDriveTokenStorage();
                    return false;
                }
                driveAccessToken = parsed.token;
                driveTokenExpiry = parsed.expiry;
                scheduleDriveTokenRefresh();
                return true;
            } catch (e) {
                console.error('Failed to load Drive token:', e);
                return false;
            }
        }
