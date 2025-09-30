import { useState } from "react";
import { motion } from "framer-motion";
import { Brain, Sparkles } from "lucide-react";
import { Card, CardContent } from "./ui/card";
import { Button } from "./ui/button";
import { PRIORITY_COLORS } from "../constants/config";
import { cn } from "../lib/utils";
import type { InsightPriority, InsightCategory } from "../types";

interface InsightItem {
  title: string;
  message: string;
  action: string;
  priority: InsightPriority;
  category: InsightCategory;
  icon: React.JSX.Element;
  agentName?: string;
  confidence?: number;
  reasoning?: string;
}

interface InsightCardProps {
  item: InsightItem;
  onAccept: (item: InsightItem) => void;
  onDismiss?: (item: InsightItem) => void;
}

/**
 * InsightCard - Displays a single AI-generated insight
 */
export function InsightCard({ item, onAccept, onDismiss }: InsightCardProps) {
  const [expanded, setExpanded] = useState(false);
  const [dismissed, setDismissed] = useState(false);

  const handleDismiss = () => {
    setDismissed(true);
    if (onDismiss) {
      // Call parent handler after animation
      setTimeout(() => onDismiss(item), 300);
    }
  };

  if (dismissed) {
    return (
      <motion.div 
        initial={{ opacity: 1, height: "auto" }} 
        animate={{ opacity: 0, height: 0 }}
        transition={{ duration: 0.3 }}
      />
    );
  }

  return (
    <motion.div initial={{ opacity: 0, y: 10 }} animate={{ opacity: 1, y: 0 }}>
      <Card className="bg-neutral-900 border border-neutral-800 rounded-2xl shadow-lg">
        <CardContent className="flex items-center gap-4 p-4">
          {/* Icon */}
          <div className="w-10 h-10 flex items-center justify-center rounded-lg bg-neutral-800">
            {item.icon}
          </div>

          {/* Content */}
          <div className="flex-1">
            <h3 className="text-lg font-semibold">{item.title}</h3>
            <p className="text-neutral-400 text-sm">{item.message}</p>

            {/* Metadata badges */}
            <div className="mt-2 flex items-center gap-2 flex-wrap">
              {item.priority && (
                <span className={cn(
                  "text-xs px-2 py-0.5 rounded-full border",
                  PRIORITY_COLORS[item.priority]
                )}>
                  {item.priority}
                </span>
              )}

              {item.agentName && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-purple-900/30 text-purple-400 border border-purple-800/50">
                  {item.agentName}
                </span>
              )}

              {item.confidence && (
                <span className="text-xs px-2 py-0.5 rounded-full bg-neutral-800 text-neutral-400">
                  {Math.round(item.confidence * 100)}% confidence
                </span>
              )}

              {item.reasoning && (
                <button
                  onClick={() => setExpanded(!expanded)}
                  className="text-xs text-blue-400 hover:text-blue-300 transition-colors flex items-center gap-1"
                >
                  <Brain className="w-3 h-3" />
                  {expanded ? 'Hide reasoning' : 'Why this?'}
                </button>
              )}
            </div>
          </div>

          {/* Actions */}
          <div className="flex flex-col gap-2">
            <Button variant="secondary" className="rounded-xl" onClick={() => onAccept(item)}>
              {item.action}
            </Button>
            <Button variant="ghost" className="text-xs" onClick={handleDismiss}>
              Dismiss
            </Button>
          </div>
        </CardContent>

        {/* Expandable reasoning section */}
        {expanded && item.reasoning && (
          <motion.div
            initial={{ opacity: 0, height: 0 }}
            animate={{ opacity: 1, height: "auto" }}
            className="px-4 pb-4"
          >
            <div className="bg-neutral-800/50 rounded-xl p-3 border border-neutral-700">
              <div className="flex items-start gap-2">
                <div className="w-1 h-full bg-blue-400 rounded-full"></div>
                <div className="flex-1">
                  <div className="text-xs text-neutral-400 mb-1 flex items-center gap-1">
                    <Sparkles className="w-3 h-3" />
                    AI Reasoning
                  </div>
                  <p className="text-sm text-neutral-300">{item.reasoning}</p>
                </div>
              </div>
            </div>
          </motion.div>
        )}
      </Card>
    </motion.div>
  );
}
