import { Sidebar } from "@/components/layout/sidebar";
import { Header } from "@/components/layout/header";
import { MobileNav } from "@/components/layout/mobile-nav";
import { Toaster } from "sonner";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen w-full bg-slate-100/90 dark:bg-slate-950 print:bg-white pb-16 lg:pb-0">
      <div className="print:hidden flex">
        <Sidebar />
      </div>
      <div className="flex flex-1 flex-col min-w-0">
        <div className="print:hidden">
          <Header />
        </div>
        <main id="main" className="flex-1 p-4 md:p-6 lg:p-8 max-w-7xl w-full mx-auto print:p-0">
          {children}
        </main>
      </div>
      <MobileNav />
      <Toaster position="top-right" richColors closeButton />
    </div>
  );
}
