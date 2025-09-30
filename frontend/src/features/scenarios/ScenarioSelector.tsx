import { motion } from "framer-motion";
import { Sparkles } from "lucide-react";
import type { Scenario } from "../../types";

interface ScenarioSelectorProps {
  scenarios: Scenario[];
  selectedScenario: string | null;
  onScenarioSelect: (scenarioId: string | null) => void;
}

/**
 * ScenarioSelector - Allows users to select different scenarios
 */
export function ScenarioSelector({ 
  scenarios, 
  selectedScenario, 
  onScenarioSelect 
}: ScenarioSelectorProps) {
  if (!scenarios || scenarios.length === 0) return null;

  const selectedScenarioData = scenarios.find(s => s.id === selectedScenario);

  return (
    <div className="flex flex-col gap-3 relative z-10">
      {/* Header */}
      <div className="flex items-center justify-between">
        <div className="flex items-center gap-2">
          <h3 className="text-sm font-medium text-neutral-400">Select Context</h3>
          <span className="text-xs px-2 py-0.5 rounded-full bg-purple-900/30 text-purple-400 border border-purple-800/50">
            Demo Mode
          </span>
        </div>
        {selectedScenario && (
          <button
            onClick={() => onScenarioSelect(null)}
            className="text-xs text-blue-400 hover:text-blue-300"
          >
            Auto-detect
          </button>
        )}
      </div>

      {/* Scenario buttons */}
      <div className="flex gap-2 overflow-x-auto pb-2 scrollbar-hide pt-2 -mt-2">
        {scenarios.map(scenario => (
          <ScenarioButton
            key={scenario.id}
            scenario={scenario}
            isSelected={selectedScenario === scenario.id}
            onSelect={onScenarioSelect}
          />
        ))}
      </div>

      {/* Selected scenario info */}
      {selectedScenario && selectedScenarioData && (
        <motion.div
          initial={{ opacity: 0, y: -10 }}
          animate={{ opacity: 1, y: 0 }}
          className="bg-blue-900/20 border border-blue-800/50 rounded-xl p-3"
        >
          <div className="flex items-center gap-2">
            <Sparkles className="w-4 h-4 text-blue-400" />
            <span className="text-sm text-blue-300">
              Manual mode: {selectedScenarioData.description}
            </span>
          </div>
        </motion.div>
      )}
    </div>
  );
}

interface ScenarioButtonProps {
  scenario: Scenario;
  isSelected: boolean;
  onSelect: (scenarioId: string) => void;
}

/**
 * ScenarioButton - Individual scenario button
 */
function ScenarioButton({ scenario, isSelected, onSelect }: ScenarioButtonProps) {
  return (
    <motion.button
      onClick={() => onSelect(scenario.id)}
      whileHover={{ scale: 1.05 }}
      whileTap={{ scale: 0.95 }}
      className={`relative flex flex-col items-center justify-center min-w-[80px] h-20 rounded-xl border-2 transition-all ${
        isSelected
          ? 'bg-blue-500/20 border-blue-500 shadow-lg shadow-blue-500/20'
          : 'bg-neutral-900 border-neutral-800 hover:border-neutral-700'
      }`}
    >
      <span className="text-2xl mb-1">{scenario.icon}</span>
      <span className="text-xs font-medium">{scenario.name}</span>
      {isSelected && (
        <motion.div
          initial={{ scale: 0 }}
          animate={{ scale: 1 }}
          className="absolute -top-1 -right-1 w-3 h-3 bg-blue-500 rounded-full"
        />
      )}
    </motion.button>
  );
}
