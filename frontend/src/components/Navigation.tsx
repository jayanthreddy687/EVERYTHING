import { Sparkles, Calendar, Users, LucideIcon } from "lucide-react";
import { cn } from "../lib/utils";
import type { TabType } from "../constants/config";

interface NavItem {
  id: TabType;
  icon: LucideIcon;
  label: string;
}

const NAV_ITEMS: NavItem[] = [
  { id: "now", icon: Sparkles, label: "Now" },
  { id: "agenda", icon: Calendar, label: "Agenda" },
  { id: "profile", icon: Users, label: "Profile" },
];

interface NavigationProps {
  activeTab: TabType;
  onTabChange: (tab: TabType) => void;
}

/**
 * Bottom navigation component
 */
export function Navigation({ activeTab, onTabChange }: NavigationProps) {
  return (
    <nav className="fixed bottom-0 left-0 w-full bg-neutral-950 border-t border-neutral-800 flex justify-around py-3">
      {NAV_ITEMS.map((item) => {
        const Icon = item.icon;
        const isActive = activeTab === item.id;

        return (
          <button
            key={item.id}
            onClick={() => onTabChange(item.id)}
            className={cn(
              "flex flex-col items-center gap-1 transition-colors",
              isActive ? "text-white" : "text-neutral-500"
            )}
          >
            <Icon className="w-5 h-5" />
            <span className="text-sm">{item.label}</span>
          </button>
        );
      })}
    </nav>
  );
}
