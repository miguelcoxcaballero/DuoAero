package com.duoaero.nativebase;
import android.app.Instrumentation;
import android.content.Intent;
import android.os.Bundle;
import java.lang.reflect.Method;

/** Launches the original offline-session entry point, without rebuilding its screen. */
public final class SessionProbe extends Instrumentation {
    public void onCreate(Bundle args) { start(); }
    public void onStart() {
        Bundle result = new Bundle();
        try {
            ClassLoader loader = getTargetContext().getClassLoader();
            Class<?> activity = Class.forName("com.duolingo.session.SessionActivity", true, loader);
            Class<?> params = Class.forName("com.duolingo.data.session.start.SessionStartParams$Hardcoded", true, loader);
            Object session = params.getConstructor(String.class, boolean.class)
                .newInstance("hardcoded_sessions/math/math_lesson.json", false);
            Object via = Class.forName("com.duolingo.data.onboarding.OnboardingVia", true, loader).getField("HOME").get(null);
            Method factory = null;
            for (Method method : activity.getDeclaredMethods()) {
                if (method.getName().equals("L") && method.getParameterTypes().length == 13) factory = method;
            }
            if (factory == null) throw new NoSuchMethodException("Original SessionActivity intent factory");
            Intent intent = (Intent) factory.invoke(null, getTargetContext(), session, false, via,
                false, false, null, null, null, true, false, null, activity);
            getTargetContext().startActivity(intent.addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            Thread.sleep(45000);
            result.putString("stream", "Original offline session requested; inspect the visible screen and logs.\n");
        } catch (Throwable failure) {
            result.putString("stream", android.util.Log.getStackTraceString(failure));
        }
        finish(-1, result);
    }
}
