<script>
  import { setContext } from "svelte";
  import { writable } from "svelte/store";

  import {
    set,
    setMode,
    failuresSetMode,
    histogramSets,
    brushSet,
  } from "./store.js";

  import { json } from "d3-fetch";

  import Histogram from "./graphics/Histogram.svelte";
  import Map from "./graphics/Map.svelte";

  import GRIT from "./GRIT.svelte";

  import Router from "svelte-spa-router";
  import { wrap } from "svelte-spa-router/wrap";

  const history = writable([]);
  const waypoints = writable([]);
  const summary = writable([]);
  const failures = writable([]);
  const simIds = writable([]);
  setContext("history", history);
  setContext("waypoints", waypoints);
  setContext("summary", summary);
  setContext("failures", failures);
  setContext("simIds", simIds);



  setContext("colormap", ['#316939','#748C38','#FFED63','#CF7F29','#753F3C']);



  // setContext("failureColor", "#006e2e");
  setContext("failureColor", "#823519");
  // setContext("successColor", "#9bdd8c");
  setContext("successColor", "#5C92CC");
  setContext("pathOpacity", 0.5);

  function computeTotalSet(failureSetMode, histogramSets, brushSet) {
    let allSet = $simIds.map(() => true);

    Object.keys(histogramSets).map((attr) => {
      allSet = allSet.map((b, i) => b && histogramSets[attr][i]);
    });

    allSet = allSet.map((b, i) => b && !brushSet[i]);

    set.set(allSet);
  }

  histogramSets.subscribe((v) => {
    computeTotalSet($failuresSetMode, v, $brushSet);
  });

  brushSet.subscribe((v) => {
    computeTotalSet($failuresSetMode, $histogramSets, v);
  });

  const params = new Proxy(new URLSearchParams(window.location.search), {
    get: (searchParams, prop) => searchParams.get(prop),
  });
  // Get the value of "some_key" in eg "https://example.com/?some_key=some_value"
  let simFolder = params.data; 
  setContext("simFolder", simFolder)

  let cfaFile = '';
  let demFile = '';
  if (!params.cfa) {
    cfaFile = "cfa";
  } else { cfaFile = params.cfa; }

  if (!params.dem) {
    demFile = "dem";
  } else { demFile = params.dem; }

  setContext("cfa", cfaFile)
  setContext("dem", demFile)


  async function fetchData() {
    const result = await Promise.all([
      json("/"+simFolder+"/history.json"),
      json("/"+simFolder+"/wp.json"),
      json("/"+simFolder+"/summary.json"),
    ]).then(([processedHistory, processedWaypoints, processedSummary]) => {
      history.set(processedHistory);
      waypoints.set(processedWaypoints);
      summary.set(processedSummary);

      let processedFailures = processedSummary.map((v) => v.failure);
      failures.set(processedFailures);

      let processedSimIds = processedSummary.map((v) => v.simId);
      simIds.set(processedSimIds);
      if (
        JSON.stringify($set) !== JSON.stringify(processedSimIds) ||
        $set.length <= 0
      ) {
        set.set(processedSimIds.map(() => true));
      }

      return true;
    });

    return result;
  }

  const routes = {
    "/": wrap({
      component: GRIT,
    }),
    "/histogram": wrap({
      component: Histogram,
      props: {
        x: "slip",
      },
    }),
    "/map": wrap({
      component: Map,
      props: {
        val: "history",
        x: "ROVER_X",
        y: "ROVER_Y",
      },
    })
  };
</script>

<div class="container">
  {#await fetchData() then c}
    <svelte:component this={Router} {routes} />
  {/await}
</div>

<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.1.1/css/all.min.css" />
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Cairo&display=swap" rel="stylesheet">


<style>
  @tailwind base;
  @tailwind components;
  @tailwind utilities;
  @import url('https://fonts.googleapis.com/css2?family=Cairo&display=swap');

  .container {
    width: auto;
    height: 200px;
    max-width: none;
  }
</style>
