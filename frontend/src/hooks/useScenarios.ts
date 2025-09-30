import { useState, useEffect } from 'react';
import { apiService } from '../services/api';
import type { Scenario } from '../types';

interface UseScenariosReturn {
  availableScenarios: Scenario[];
  selectedScenario: string | null;
  selectScenario: (scenarioId: string | null) => void;
}

/**
 * Hook for managing scenario selection
 */
export function useScenarios(): UseScenariosReturn {
  const [availableScenarios, setAvailableScenarios] = useState<Scenario[]>([]);
  const [selectedScenario, setSelectedScenario] = useState<string | null>(null);

  useEffect(() => {
    fetchScenarios();
  }, []);

  async function fetchScenarios(): Promise<void> {
    try {
      const data = await apiService.getScenarios();
      setAvailableScenarios(data.scenarios || []);
    } catch (e) {
      console.error("Failed to fetch scenarios:", e);
    }
  }

  function selectScenario(scenarioId: string | null): void {
    if (scenarioId === null) {
      setSelectedScenario(null);
    } else {
      setSelectedScenario(prevSelected => 
        prevSelected === scenarioId ? null : scenarioId
      );
    }
  }

  return {
    availableScenarios,
    selectedScenario,
    selectScenario
  };
}
