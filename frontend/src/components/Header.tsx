import { Settings } from "lucide-react";
import { Button } from "./ui/button";
import { APP_CONFIG } from "../constants/config";
import type { AgentStats } from "../types";

interface HeaderProps {
  agentStats: AgentStats | null;
  onRefresh: () => void;
}

/**
 * Header component with app title and agent stats
 */
export function Header({ agentStats, onRefresh }: HeaderProps) {
  return (
    <header className="flex items-center justify-between">
      <div>
        <h1 className="text-2xl font-bold tracking-tight">{APP_CONFIG.APP_NAME}</h1>
        <p className="text-neutral-400 text-sm">{APP_CONFIG.APP_TAGLINE}</p>
      </div>

      <div className="flex items-center gap-3">
        {agentStats && (
          <div className="text-xs text-neutral-400 mr-2 flex items-center gap-2">
            <div className="w-2 h-2 bg-green-400 rounded-full animate-pulse"></div>
            {agentStats.activeAgents} agents
          </div>
        )}
        <Button variant="ghost" onClick={onRefresh}>
          <Settings className="w-4 h-4" />
        </Button>
      </div>
    </header>
  );
}
