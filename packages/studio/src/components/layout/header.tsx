"use client";

import { Sun, Moon, Monitor, Search, Command } from "lucide-react";
import { useAppStore } from "@/stores/app-store";
import { Button } from "@/components/ui/button";
import { Avatar, AvatarFallback } from "@/components/ui/avatar";
import { Badge } from "@/components/ui/badge";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuLabel,
  DropdownMenuSeparator,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Input } from "@/components/ui/input";
import { NotificationCenter } from "@/components/layout/notification-center";
import { ActivityIndicator } from "@/components/studio/activity-indicator";

export function Header() {
  const { theme, setTheme, user, currentWorkspace } = useAppStore();

  return (
    <header className="flex h-11 items-center gap-3 border-b bg-studio-card px-4">
      <div className="flex items-center gap-2">
        {currentWorkspace && (
          <>
            <Badge variant="outline" className="text-[10px] px-2 py-0 h-5">
              {currentWorkspace.name}
            </Badge>
            <Badge variant="secondary" className="text-[10px] px-2 py-0 h-5">
              {currentWorkspace.environment}
            </Badge>
          </>
        )}
        <div className="ml-2">
          <ActivityIndicator />
        </div>
      </div>

      <div className="flex-1" />

      <div className="hidden sm:flex relative max-w-xs flex-1">
        <Search className="absolute left-2.5 top-1/2 h-3.5 w-3.5 -translate-y-1/2 text-muted-foreground" />
        <Input placeholder="Search studio... (Ctrl+K)" className="pl-8 h-8 text-xs bg-muted/50" />
      </div>

      <NotificationCenter />

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" size="icon" className="h-8 w-8">
            <Sun className="h-3.5 w-3.5 rotate-0 scale-100 transition-all dark:-rotate-90 dark:scale-0" />
            <Moon className="absolute h-3.5 w-3.5 rotate-90 scale-0 transition-all dark:rotate-0 dark:scale-100" />
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent align="end">
          <DropdownMenuItem onClick={() => setTheme("light")}>
            <Sun className="mr-2 h-4 w-4" /> Light
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("dark")}>
            <Moon className="mr-2 h-4 w-4" /> Dark
          </DropdownMenuItem>
          <DropdownMenuItem onClick={() => setTheme("system")}>
            <Monitor className="mr-2 h-4 w-4" /> System
          </DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>

      <DropdownMenu>
        <DropdownMenuTrigger asChild>
          <Button variant="ghost" className="relative h-8 w-8 rounded-full" size="icon">
            <Avatar className="h-8 w-8">
              <AvatarFallback className="bg-primary/10 text-primary text-xs">
                {user?.name?.charAt(0) || "U"}
              </AvatarFallback>
            </Avatar>
          </Button>
        </DropdownMenuTrigger>
        <DropdownMenuContent className="w-56" align="end">
          <DropdownMenuLabel>
            <div className="flex flex-col">
              <span className="text-sm">{user?.name || "User"}</span>
              <span className="text-xs font-normal text-muted-foreground">{user?.email || ""}</span>
              <span className="text-[10px] font-normal text-muted-foreground mt-0.5">{user?.role}</span>
            </div>
          </DropdownMenuLabel>
          <DropdownMenuSeparator />
          <DropdownMenuItem>Profile</DropdownMenuItem>
          <DropdownMenuItem>Settings</DropdownMenuItem>
          <DropdownMenuSeparator />
          <DropdownMenuItem className="text-destructive">Sign Out</DropdownMenuItem>
        </DropdownMenuContent>
      </DropdownMenu>
    </header>
  );
}
