package com.duoaero.nativebase;

import android.app.Activity;
import android.app.Instrumentation;
import android.content.Intent;
import android.os.Bundle;
import android.view.View;
import android.widget.LinearLayout;
import android.widget.ScrollView;
import java.lang.reflect.Method;

/** Diagnostic only: exercises the reference APK's actual Compose LaTeX view. */
public final class LatexProbe extends Instrumentation {
    public void onCreate(Bundle args) { start(); }
    public void onStart() {
        final Bundle result = new Bundle();
        try {
            final java.util.concurrent.atomic.AtomicReference<Activity> shown = new java.util.concurrent.atomic.AtomicReference<>();
            final java.util.concurrent.CountDownLatch resumed = new java.util.concurrent.CountDownLatch(1);
            ((android.app.Application)getTargetContext().getApplicationContext()).registerActivityLifecycleCallbacks(new android.app.Application.ActivityLifecycleCallbacks() {
                public void onActivityResumed(Activity a) { shown.set(a); resumed.countDown(); }
                public void onActivityCreated(Activity a, Bundle b) {}
                public void onActivityStarted(Activity a) {}
                public void onActivityPaused(Activity a) {}
                public void onActivityStopped(Activity a) {}
                public void onActivitySaveInstanceState(Activity a, Bundle b) {}
                public void onActivityDestroyed(Activity a) {}
            });
            getTargetContext().startActivity(new Intent().setClassName(getTargetContext(), "com.duolingo.splash.LaunchActivity").addFlags(Intent.FLAG_ACTIVITY_NEW_TASK));
            if (!resumed.await(15, java.util.concurrent.TimeUnit.SECONDS)) throw new IllegalStateException("Original activity did not resume");
            Thread.sleep(3000);
            final Activity activity = shown.get();
            runOnMainSync(() -> {
                try {
                    Class<?> cls = Class.forName("com.duolingo.feature.math.ui.figure.MathLatexView",
                        true, getTargetContext().getClassLoader());
                    ScrollView scroll = new ScrollView(activity);
                    LinearLayout column = new LinearLayout(activity);
                    column.setOrientation(LinearLayout.VERTICAL);
                    column.setPadding(24, 100, 24, 40);
                    scroll.addView(column);
                    Method latex = cls.getMethod("setLatexString", String.class);
                    for (String expression : new String[] {
                        "V_s=\\sqrt{\\frac{2W}{\\rho S C_{L,\\max}}}",
                        "R=\\frac{V}{g c_e}\\frac{L}{D}\\ln\\left(\\frac{m_i}{m_f}\\right)",
                        "P_{cr}=\\frac{\\pi^2 EI}{(KL)^2}",
                        "\\frac{C_{L,2}}{C_{L,1}}=\\frac{\\rho_1}{\\rho_2}"
                    }) {
                        View view = (View) cls.getConstructor(android.content.Context.class).newInstance(activity);
                        cls.getMethod("setFontSizeDp", float.class).invoke(view, 24f);
                        cls.getMethod("setGlobalColor", Integer.class).invoke(view, Integer.valueOf(0xff3c3c3c));
                        latex.invoke(view, expression);
                        column.addView(view, new LinearLayout.LayoutParams(-1, 180));
                    }
                    scroll.setBackgroundColor(0xffffffff);
                    activity.setContentView(scroll);
                    result.putString("stream", "Original MathLatexView attached; visual verification required.\n");
                } catch (Throwable failure) {
                    result.putString("stream", android.util.Log.getStackTraceString(failure));
                }
            });
            // Leave the diagnostic visible for user-interface inspection; this is not a release screen.
            Thread.sleep(45000);
        } catch (Throwable failure) {
            result.putString("stream", android.util.Log.getStackTraceString(failure));
        }
        finish(-1, result);
    }
}
