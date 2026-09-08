'use client';

import { useState } from 'react';
import { useRouter } from 'next/navigation';
import { useTheme } from 'next-themes';
import { motion } from 'framer-motion';
import {
  Menu, Search, Bell, Sun, Moon, User, Settings,
  LogOut, Globe, ChevronDown, Command,
} from 'lucide-react';
import { Button } from '@/components/ui/button';
import { Avatar, AvatarFallback, AvatarImage } from '@/components/ui/avatar';
import { Separator } from '@/components/ui/separator';
import {
  DropdownMenu, DropdownMenuContent, DropdownMenuItem,
  DropdownMenuLabel, DropdownMenuSeparator, DropdownMenuTrigger,
} from '@/components/ui/dropdown-menu';
import { useChatStore } from '@/features/chat/store';

interface HeaderProps {
  onMenuToggle: () => void;
  onCommandOpen: () => void;
}

export function Header({ onMenuToggle, onCommandOpen }: HeaderProps) {
  const { theme, setTheme } = useTheme();
  const connected = useChatStore((s) => s.connected);

  return (
    <header className="sticky top-0 z-30 flex h-16 items-center gap-4 border-b border-white/5 bg-[hsl(222,47%,8%)]/80 px-4 backdrop-blur-xl lg:px-6">
      <Button variant="ghost" size="icon" onClick={onMenuToggle} className="h-9 w-9 lg:hidden">
        <Menu className="h-5 w-5" />
      </Button>

      <div className="hidden items-center gap-2 lg:flex">
        <div className="flex h-8 w-8 items-center justify-center rounded-lg bg-gradient-to-br from-blue-500/20 to-cyan-500/20 border border-blue-500/10">
          <Command className="h-4 w-4 text-blue-400" />
        </div>
        <span className="text-sm font-semibold bg-gradient-to-r from-blue-400 to-cyan-400 bg-clip-text text-transparent">
          JARVIS Command Center
        </span>
      </div>

      <div className="flex-1 md:max-w-xl">
        <Button
          variant="outline"
          className="w-full justify-start gap-2 text-sm text-muted-foreground/50 h-9 font-normal bg-white/[0.02] border-white/5 hover:bg-white/5"
          onClick={onCommandOpen}
        >
          <Search className="h-4 w-4" />
          <span className="flex-1 text-left">Search commands, knowledge, agents...</span>
          <kbd className="pointer-events-none ml-auto inline-flex h-5 select-none items-center gap-1 rounded border border-white/10 bg-white/5 px-1.5 font-mono text-[10px] font-medium text-muted-foreground/60">
            <Command className="h-3 w-3" />K
          </kbd>
        </Button>
      </div>

      <div className="flex items-center gap-2">
        <div className="flex items-center gap-1.5 rounded-full border border-white/5 bg-white/[0.02] px-3 py-1">
          <span className={`inline-flex h-2 w-2 rounded-full ${connected ? 'bg-emerald-500' : 'bg-red-500'}`} />
          <span className="text-[10px] font-medium text-muted-foreground/50">
            {connected ? 'Connected' : 'Offline'}
          </span>
        </div>

        <Button variant="ghost" size="icon" className="h-9 w-9 relative text-muted-foreground/60 hover:text-foreground">
          <Bell className="h-5 w-5" />
          <span className="absolute -right-0.5 -top-0.5 flex h-4 w-4 items-center justify-center rounded-full bg-gradient-to-r from-blue-500 to-cyan-400 text-[10px] font-bold text-white">3</span>
        </Button>

        <Button
          variant="ghost"
          size="icon"
          className="h-9 w-9 text-muted-foreground/60 hover:text-foreground transition-all hover:scale-110"
          onClick={() => setTheme(theme === 'dark' ? 'light' : 'dark')}
        >
          <motion.div
            initial={false}
            animate={{ rotate: theme === 'dark' ? 0 : 180 }}
            transition={{ duration: 0.3 }}
          >
            {theme === 'dark' ? (
              <Sun className="h-5 w-5 text-amber-400" />
            ) : (
              <Moon className="h-5 w-5 text-blue-400" />
            )}
          </motion.div>
        </Button>

        <Separator orientation="vertical" className="h-6 bg-white/5" />

        <DropdownMenu>
          <DropdownMenuTrigger asChild>
            <Button variant="ghost" className="h-9 gap-2 px-2">
              <Avatar className="h-7 w-7 ring-2 ring-blue-500/20">
                <AvatarImage src="/avatars/default.png" alt="User" />
                <AvatarFallback className="bg-gradient-to-br from-blue-500 to-cyan-400 text-white text-xs font-bold">A</AvatarFallback>
              </Avatar>
              <div className="hidden text-left md:block">
                <span className="block text-sm font-medium">Admin</span>
                <span className="block text-[10px] text-muted-foreground/50">admin@jarvis.local</span>
              </div>
              <ChevronDown className="ml-1 h-3 w-3 text-muted-foreground/40 hidden md:block" />
            </Button>
          </DropdownMenuTrigger>
          <DropdownMenuContent align="end" className="w-56 bg-[hsl(222,47%,12%)] border-white/10">
            <DropdownMenuLabel>
              <div className="flex flex-col">
                <span className="font-medium">Admin</span>
                <span className="text-xs text-muted-foreground/50">admin@jarvis.local</span>
              </div>
            </DropdownMenuLabel>
            <DropdownMenuSeparator className="bg-white/5" />
            <DropdownMenuItem><User className="mr-2 h-4 w-4" />Profile</DropdownMenuItem>
            <DropdownMenuItem><Settings className="mr-2 h-4 w-4" />Settings</DropdownMenuItem>
            <DropdownMenuItem><Globe className="mr-2 h-4 w-4" />API Docs</DropdownMenuItem>
            <DropdownMenuSeparator className="bg-white/5" />
            <DropdownMenuItem className="text-red-400 focus:text-red-400 focus:bg-red-500/10">
              <LogOut className="mr-2 h-4 w-4" />Sign out
            </DropdownMenuItem>
          </DropdownMenuContent>
        </DropdownMenu>
      </div>
    </header>
  );
}
