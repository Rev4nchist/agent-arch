import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Fourth AI Architecture Hub",
  description: "Microsoft Agent Framework Architecture & Governance Portal",
};

export default function LandingLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
