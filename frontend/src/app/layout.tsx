import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Navbar } from "@/components/layout/Navbar";
import { Footer } from "@/components/layout/Footer";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "VERIDEX | AI-Powered Identity Intelligence",
  description: "Identity and document screening for detecting inconsistencies, manipulation, and identity mismatch.",
};

import { AuthProvider } from "@/contexts/AuthContext";
import { ToastProvider } from "@/contexts/ToastContext";
import { MouseLight } from "@/components/ui/MouseLight";
import { AnimatedDocumentBackground } from "@/components/background/AnimatedDocumentBackground";

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased min-h-screen bg-[#090a0c] text-foreground`}
        suppressHydrationWarning
      >
        <AuthProvider>
          <ToastProvider>
            {/* BACKGROUND LAYER (z-0) */}
            <div id="background-layer" className="fixed inset-0 z-0 pointer-events-none overflow-hidden">
              {/* Ambient Interface System */}
              <div className="absolute inset-0 bg-[linear-gradient(to_right,rgba(255,255,255,0.02)_1px,transparent_1px),linear-gradient(to_bottom,rgba(255,255,255,0.02)_1px,transparent_1px)] bg-[size:3rem_3rem]" />
              <div className="absolute top-0 left-[-10%] w-[40%] h-[40%] rounded-full bg-primary/10 blur-[120px]" />
              <div className="absolute bottom-[-10%] right-[-10%] w-[40%] h-[40%] rounded-full bg-violet-600/10 blur-[120px]" />
              
              <AnimatedDocumentBackground />
            </div>

            {/* APPLICATION LAYER (z-10) */}
            <div id="application-layer" className="relative z-10 flex flex-col min-h-screen">
              <MouseLight />
              <Navbar />
              <main className="flex-1 relative">
                {children}
              </main>
              <Footer />
            </div>
          </ToastProvider>
        </AuthProvider>
      </body>
    </html>
  );
}
