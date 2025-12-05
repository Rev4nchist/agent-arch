import Sidebar from "@/components/Sidebar";
import { AccessGuard } from "@/components/auth";
import { GuideProvider } from "@/components/providers/GuideProvider";
import { GuideWidget } from "@/components/guide";

export default function AuthenticatedLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <AccessGuard>
      <GuideProvider>
        <Sidebar />
        <main className="pl-64">
          {children}
        </main>
        <GuideWidget />
      </GuideProvider>
    </AccessGuard>
  );
}
