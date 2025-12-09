import type { Metadata } from "next";

export const metadata: Metadata = {
  title: "Fourth AI Showcase | Microsoft AI Ecosystem",
  description: "Discover how Fourth leverages the Microsoft AI Ecosystem to build intelligent business automation",
};

export default function ShowcaseLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return children;
}
