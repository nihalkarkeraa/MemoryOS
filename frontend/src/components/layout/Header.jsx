import React from "react";
import { Search, Bell, Menu, ChevronRight } from "lucide-react";
import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";

export default function Header({ title, onOpenSidebar }) {
  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-3 border-b border-border bg-background/80 px-4 backdrop-blur-xl sm:px-6">
      <Button
        variant="ghost"
        size="icon"
        className="lg:hidden"
        onClick={onOpenSidebar}
      >
        <Menu className="h-5 w-5" />
      </Button>

      {/* Breadcrumb / title */}
      <div className="flex min-w-0 items-center gap-2">
        <span className="hidden text-[13px] text-muted-foreground sm:inline">MemoryOS</span>
        <ChevronRight className="hidden h-3.5 w-3.5 text-muted-foreground/50 sm:inline" />
        <h1 className="truncate text-[15px] font-semibold tracking-tight text-foreground">
          {title}
        </h1>
      </div>

      <div className="ml-auto flex items-center gap-1.5">
        {/* Search trigger (placeholder) */}
        <Button variant="ghost" size="icon" className="text-muted-foreground hover:text-foreground">
          <Search className="h-[18px] w-[18px]" />
        </Button>

        {/* Notifications */}
        <Button variant="ghost" size="icon" className="relative text-muted-foreground hover:text-foreground">
          <Bell className="h-[18px] w-[18px]" />
          <span className="absolute right-2.5 top-2.5 h-1.5 w-1.5 rounded-full bg-primary" />
        </Button>

        <div className="mx-1 h-6 w-px bg-border" />

        {/* User menu */}
        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <button className="flex items-center gap-2 rounded-full p-0.5 transition-colors hover:bg-muted/60">
              <Avatar className="h-8 w-8 border border-border">
                <AvatarFallback className="bg-gradient-to-br from-violet-500 to-indigo-600 text-[12px] font-semibold text-white">
                  MO
                </AvatarFallback>
              </Avatar>
            </button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56">
            <DropdownMenuLabel className="flex flex-col gap-0.5">
              <span className="text-[13px] font-medium">MemoryOS User</span>
              <span className="text-[11px] font-normal text-muted-foreground">user@memoryos.app</span>
            </DropdownMenuLabel>
            <DropdownMenuSeparator />
            <DropdownMenuItem>Profile</DropdownMenuItem>
            <DropdownMenuItem>Preferences</DropdownMenuItem>
            <DropdownMenuItem>Keyboard shortcuts</DropdownMenuItem>
            <DropdownMenuSeparator />
            <DropdownMenuItem className="text-destructive">Sign out</DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}