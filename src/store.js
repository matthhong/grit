import { writable } from 'svelte/store';

const createWritableStore = (key, startValue) => {
    const { subscribe, set, update } = writable(startValue);
    
    return {
      subscribe,
      set,
      update,
      useLocalStorage: () => {
        const json = localStorage.getItem(key);
        if (json) {
          set(JSON.parse(json));
        }
        
        subscribe(current => {
          localStorage.setItem(key, JSON.stringify(current));
        });
      }
    };
  }

export const set = createWritableStore('set', []);
export const setMode = createWritableStore('setMode', 'all');
export const failuresSetMode = createWritableStore('failuresSetMode', 'out');
export const histogramSets = createWritableStore('histogramSets', {})
export const brushSet = createWritableStore('brushSet', [])