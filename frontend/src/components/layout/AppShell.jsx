import React, { useState } from "react";
import { Outlet, useLocation } from "react-router-dom";
import Sidebar from "./Sidebar";
import Header from "./Header";

const titleMap = {
  "/home": "Home",
  "/documents": "Documents",
  "/search": "Search",
  "/compare": "Compare",
  "/summaries": "Summaries",
};

export default function AppShell() {
  const [collapsed, setCollapsed] = useState(false);
  const [mobileOpen, setMobileOpen] = useState(false);
  const location = useLocation();
  const title = titleMap[location.pathname] || "Home";

  return (
    <div className="flex h-screen w-full overflow-hidden bg-background">
      <Sidebar
        collapsed={collapsed}
        onToggle={() => setCollapsed((c) => !c)}
        mobileOpen={mobileOpen}
        onMobileClose={() => setMobileOpen(false)}
      />
      <div className="flex min-w-0 flex-1 flex-col">
        <Header title={title} onOpenSidebar={() => setMobileOpen(true)} />
        <main className="flex-1 overflow-y-auto">
          <Outlet />
        </main>
      </div>
    </div>
  );
}