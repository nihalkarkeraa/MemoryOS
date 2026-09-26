import React from "react";
import { Link, useLocation } from "react-router-dom";
import {
  Brain,
  FileText,
  Search,
  GitCompareArrows,
  ScrollText,
  Network,
  Settings,
  ChevronLeft,
  Sparkles,
} from "lucide-react";
import { cn } from "@/lib/utils";
import { useBackendHealth } from "@/hooks/useBackendHealth";

const navSections = [
  {
    label: "Workspace",
    items: [
      {
        label: "Home",
        icon: Brain,
        to: "/home",
      },
      {
        label: "Documents",
        icon: FileText,
        to: "/documents",
      },
      {
        label: "Search",
        icon: Search,
        to: "/search",
      },
      {
        label: "Compare",
        icon: GitCompareArrows,
        to: "/compare",
      },
      {
        label: "Summaries",
        icon: ScrollText,
        to: "/summaries",
      },
      {
        label: "Knowledge Graph",
        icon: Network,
        to: "/knowledge-graph",
      },
    ],
  },
];

export default function Sidebar({
  collapsed,
  onToggle,
  mobileOpen,
  onMobileClose,
}) {
  const location = useLocation();
  const backendStatus = useBackendHealth();

  const statusColor =
    backendStatus === "connected"
      ? "bg-emerald-500"
      : backendStatus === "unavailable"
        ? "bg-rose-500"
        : "bg-amber-500";

  const statusPing =
    backendStatus === "connected"
      ? "bg-emerald-500/50"
      : backendStatus === "unavailable"
        ? "bg-rose-500/50"
        : "bg-amber-500/50";

  const statusLabel =
    backendStatus === "connected"
      ? "Backend connected"
      : backendStatus === "unavailable"
        ? "Backend unavailable"
        : "Checking backend...";

  return (
    <>
      {/* Mobile overlay */}
      <div
        className={cn(
          "fixed inset-0 z-40 bg-black/60 backdrop-blur-sm transition-opacity lg:hidden",
          mobileOpen
            ? "opacity-100"
            : "pointer-events-none opacity-0"
        )}
        onClick={onMobileClose}
      />

      <aside
        className={cn(
          "fixed z-50 flex h-full flex-col border-r border-sidebar-border bg-sidebar-background transition-[width,transform] duration-300 ease-out lg:static lg:translate-x-0",
          collapsed ? "w-[68px]" : "w-[248px]",
          mobileOpen
            ? "translate-x-0"
            : "-translate-x-full lg:translate-x-0"
        )}
      >
        {/* Brand */}
        <div className="flex h-16 items-center gap-2.5 border-b border-sidebar-border px-4">
          <div className="flex h-9 w-9 shrink-0 items-center justify-center rounded-xl bg-gradient-to-br from-violet-500 to-indigo-600 shadow-lg shadow-violet-500/20">
            <Sparkles className="h-5 w-5 text-white" />
          </div>

          {!collapsed && (
            <div className="flex flex-col leading-none">
              <span className="text-[15px] font-semibold tracking-tight text-foreground">
                MemoryOS
              </span>

              <span className="mt-0.5 text-[11px] text-muted-foreground">
                AI Knowledge OS
              </span>
            </div>
          )}
        </div>

        {/* Navigation */}
        <nav className="flex-1 space-y-6 overflow-y-auto px-3 py-5">
          {navSections.map((section) => (
            <div
              key={section.label}
              className="space-y-1.5"
            >
              {!collapsed && (
                <p className="px-2.5 pb-1 text-[11px] font-medium uppercase tracking-wider text-muted-foreground/70">
                  {section.label}
                </p>
              )}

              {section.items.map((item) => {
                const isActive =
                  item.to &&
                  location.pathname === item.to;

                const Icon = item.icon;

                const content = (
                  <>
                    <Icon
                      className={cn(
                        "h-[18px] w-[18px] shrink-0 transition-colors",
                        isActive
                          ? "text-primary"
                          : "text-muted-foreground group-hover:text-foreground"
                      )}
                    />

                    {!collapsed && (
                      <span
                        className={cn(
                          "flex-1 truncate text-[13.5px] font-medium transition-colors",
                          isActive
                            ? "text-foreground"
                            : "text-muted-foreground group-hover:text-foreground"
                        )}
                      >
                        {item.label}
                      </span>
                    )}
                  </>
                );

                return (
                  <Link
                    key={item.label}
                    to={item.to}
                    onClick={onMobileClose}
                    title={
                      collapsed
                        ? item.label
                        : undefined
                    }
                    className={cn(
                      "group relative flex items-center gap-3 rounded-lg px-2.5 py-2 transition-colors",
                      isActive
                        ? "bg-sidebar-accent text-foreground"
                        : "hover:bg-sidebar-accent/60"
                    )}
                  >
                    {isActive && (
                      <span className="absolute left-0 top-1/2 h-5 w-[3px] -translate-y-1/2 rounded-r-full bg-primary" />
                    )}

                    {content}
                  </Link>
                );
              })}
            </div>
          ))}
        </nav>

        {/* Footer */}
        <div className="border-t border-sidebar-border p-3">
          <div
            className={cn(
              "group flex items-center gap-3 rounded-lg px-2.5 py-2 text-muted-foreground transition-colors hover:bg-sidebar-accent/60 hover:text-foreground",
              collapsed && "justify-center"
            )}
            title={collapsed ? "Settings" : undefined}
          >
            <Settings className="h-[18px] w-[18px] shrink-0" />

            {!collapsed && (
              <span className="text-[13.5px] font-medium">
                Settings
              </span>
            )}
          </div>

          {!collapsed && (
            <div className="mb-1 flex items-center gap-2 rounded-lg px-2.5 py-2 text-[12px] text-muted-foreground">
              <span className="relative flex h-2 w-2">
                {backendStatus === "connected" && (
                  <span
                    className={cn(
                      "absolute inline-flex h-full w-full animate-ping rounded-full",
                      statusPing
                    )}
                  />
                )}

                <span
                  className={cn(
                    "relative inline-flex h-2 w-2 rounded-full",
                    statusColor
                  )}
                />
              </span>

              <span>{statusLabel}</span>
            </div>
          )}

          {collapsed && (
            <div
              className="mb-1 flex justify-center py-1.5"
              title={statusLabel}
            >
              <span className="relative flex h-2 w-2">
                {backendStatus === "connected" && (
                  <span
                    className={cn(
                      "absolute inline-flex h-full w-full animate-ping rounded-full",
                      statusPing
                    )}
                  />
                )}

                <span
                  className={cn(
                    "relative inline-flex h-2 w-2 rounded-full",
                    statusColor
                  )}
                />
              </span>
            </div>
          )}

          <button
            onClick={onToggle}
            className="mt-1 hidden w-full items-center justify-center rounded-lg px-2.5 py-2 text-muted-foreground transition-colors hover:bg-sidebar-accent/60 hover:text-foreground lg:flex"
            title={collapsed ? "Expand" : "Collapse"}
          >
            <ChevronLeft
              className={cn(
                "h-[18px] w-[18px] transition-transform",
                collapsed && "rotate-180"
              )}
            />
          </button>
        </div>
      </aside>
    </>
  );
}