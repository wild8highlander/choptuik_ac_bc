import type { Metadata } from "next";
import { Geist, Geist_Mono } from "next/font/google";
import "./globals.css";
import { Toaster } from "@/components/ui/sonner";

const geistSans = Geist({
  variable: "--font-geist-sans",
  subsets: ["latin"],
});

const geistMono = Geist_Mono({
  variable: "--font-geist-mono",
  subsets: ["latin"],
});

export const metadata: Metadata = {
  title: "Choptuik-QCD Bridge — Interactive visualization",
  description:
    "Interactive 3D/4D visualization of the 9-section Choptuik–QCD bridge monograph by Ishak Khamzatovich Isaev (ORCID 0009-0003-7299-0701).",
  keywords: [
    "Choptuik",
    "QCD",
    "strong CP problem",
    "K3 surface",
    "GUE",
    "Bayes factor",
    "Ishak Isaev",
  ],
  authors: [{ name: "Ishak Khamzatovich Isaev", url: "https://orcid.org/0009-0003-7299-0701" }],
  icons: {
    icon: "https://z-cdn.chatglm.cn/z-ai/static/logo.svg",
  },
  openGraph: {
    title: "Choptuik-QCD Bridge",
    description: "Interactive 3D/4D visualization of the 9-section Choptuik–QCD bridge monograph.",
    type: "website",
  },
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" suppressHydrationWarning>
      <body
        className={`${geistSans.variable} ${geistMono.variable} antialiased bg-background text-foreground`}
      >
        {children}
        <Toaster richColors position="top-right" />
      </body>
    </html>
  );
}
