import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Sidebar from "@/components/Sidebar";
import { GuideProvider } from "@/components/providers/GuideProvider";
import { GuideWidget } from "@/components/guide";

const inter = Inter({ subsets: ["latin"] });

export const metadata: Metadata = {
  title: "Agent Architecture Guide",
  description: "Microsoft Agent Framework Architecture & Governance Portal",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en">
      <body className={`${inter.className} antialiased`}>
        <GuideProvider>
          <Sidebar />
          <main className="pl-64">
            {children}
          </main>
          <GuideWidget />
        </GuideProvider>
      </body>
    </html>
  );
}