<script>
  import * as d3 from "d3";
  import Map from "./graphics/Map.svelte";
  import Histogram from "./graphics/Histogram.svelte";
  import Waypoints from "./graphics/Waypoints.svelte";
  import Points from "./graphics/Points.svelte";
  import Hexmap from "./graphics/Hexmap.svelte";

  import { set, failuresSetMode, setMode } from "./store.js";
  import { getContext, setContext } from "svelte";
  import { hexbin } from "d3-hexbin";

  let r = "TILT";
  let roverAttrs = ["TILT", "LEFT_DIFFERENTIAL", "RIGHT_DIFFERENTIAL"];

  let simIds = getContext("simIds");
  let failures = getContext("failures");
  let successRate;
  let filteredRate;
  let filteredRuns;
  let afterFilter;
  let numRuns = $simIds.length;
  let showCFA = false;
  let history = getContext("history");

  let cfaVal = 0;
  let xVal = 0;
  let yVal = 0;

  let truePathToggle = false;
  let waypointsToggle = true;
  let pathsToggle = false;
  let setToggle = false;
  let setOffToggle = false;
  let mapBrushToggle = false;
  let pointsToggle = false;
  let rShowToggle = false;

  let toggleStyle = "toggle-primary-content";

  let setGroup = "all";

  $: (() => {
    failuresSetMode.set(setGroup);
  })();

  $: (() => {
    setMode.set(setOffToggle ? "all" : setToggle ? "out" : "in");
  })();

  successRate = (100 * $failures.filter((v) => !v).length) / $simIds.length;

  set.subscribe((v) => {
    filteredRate = (100 * $set.filter((v) => v).length) / $simIds.length;
    filteredRuns = $set.filter((v) => v).length;

    if (filteredRuns > 0) {
      afterFilter =
        (100 * $failures.filter((v, i) => !v && $set[i]).length) /
        $set.filter((v) => v).length;
    } else {
      afterFilter = 0;
    }
  });

  const margin = {
    top: 0,
    bottom: 0,
    left: 0,
    right: 0,
  };

  let width = 600;
  let height = 600;

  let xScale = d3
    .scaleLinear()
    .domain([-30, 30])
    .nice()
    .range([margin.left, width - margin.right]);

  let yScale = d3
    .scaleLinear()
    .domain([30, -30])
    .nice()
    .range([height - margin.bottom, margin.top]);

  let rScale = d3.scaleLinear().domain([0, 60]).nice().range([0, width]);

  setContext("xScale", xScale);
  setContext("yScale", yScale);
  setContext("rScale", rScale);

  let hexRadius = 3;

  function filterTimeData(set, setMode, failuresSetMode) {
    let timeData = $history
      .filter((s, i) => {
        if (setMode == "in") {
          return set[i];
        } else if (setMode == "out") {
          return !set[i];
        }
        return true;
      })
      .filter((s, i) => {
        let simIndex = $simIds.indexOf(s.simId);
        let result = true;
        if (failuresSetMode == "in") {
          if (!$failures[simIndex]) {
            result = false;
          }
        } else if (failuresSetMode == "out") {
          if ($failures[simIndex]) {
            result = false;
          }
        }
        return result;
      })
      .map((sim, i) =>
        sim.history.map((point, j) => {
          return {
            r: point[r],
            x: point.ROVER_X,
            y: point.ROVER_Y,
            simId: sim.simId,
          };
        })
      )
      .flat();

    return timeData;
  }

  let hexed = hexbin()
    .x((d) => xScale(d.x))
    .y((d) => yScale(d.y))
    .radius((hexRadius * width) / (height - 1))
    .extent([
      [0, 0],
      [width, height],
    ]);

  setContext("hexbin", hexed);

  let bins = hexed(filterTimeData());

  let emptyBins = hexed(
    $history
      .map((sim, i) =>
        sim.history.map((point, j) => {
          return {
            r: point[r],
            x: point.ROVER_X,
            y: point.ROVER_Y,
            simId: sim.simId,
          };
        })
      )
      .flat()
  );

  $: {
    r;
    bins = hexed(filterTimeData());
  }


  $: {
    if (rShowToggle) {
      pathsToggle = true;
    } 
    else if (!rShowToggle) {
      pathsToggle = false;
    }
  }
  

  failuresSetMode.subscribe((v) => {
    bins = hexed(filterTimeData($set, $setMode, v));
  });

  set.subscribe((v) => {
    bins = hexed(filterTimeData(v, $setMode, $failuresSetMode));
  });

  setMode.subscribe((v) => {
    bins = hexed(filterTimeData($set, v, $failuresSetMode));
  });
</script>

<main
  style="--success-color: {getContext(
    'successColor'
  )}; --failure-color: {getContext('failureColor')}"
>
  <Map
    x="ROVER_X"
    y="ROVER_Y"
    bins={emptyBins}
    bind:cfaVal
    bind:xVal
    bind:yVal
    pathsToggle={!pathsToggle && !pointsToggle}
    {truePathToggle}
    {mapBrushToggle}
    {showCFA}
  >
    <Waypoints show={waypointsToggle} />
    <Points show={pointsToggle} />
    <Hexmap
      threshold={10.610674067541337}
      {bins}
      {emptyBins}
      show={pathsToggle}
      rShow={rShowToggle}
    />
  </Map>
  <div class="stats shadow stats-vertical left-side">
    <div class="stat">
      <div class="stat-title">
        <h1
          class="text-primary-content text-center"
          style="font-size:24px; letter-spacing:4px;"
        >
          GRIT
        </h1>
      </div>
    </div>
    <div class="stat">
      <div class="stat-title text-center">
        <div class="text-center">Overall <br /> Success Rate</div>
      </div>
      <div class="radial-progress" style="--value:{successRate};">
        {successRate}%
      </div>
    </div>
    <div class="stat">
      <div class="stat-title">
        <div class="text-center">Filtered <br /> Success Rate</div>
      </div>
      <div class="radial-progress" style="--value:{afterFilter};">
        {afterFilter.toFixed(0)}%
      </div>
    </div>
    <div class="stat">
      <div class="stat-title">
        <div class="text-center">Shown <br /> Simulations</div>
      </div>
      <div class="radial-progress" style="--value:{filteredRate};">
        {filteredRuns} / {numRuns}
      </div>
    </div>
  </div>

  <div class="right-side legend bg-base-100 flex">
    <div class="grid w-36 h-6 grid-cols-2 content-start">
      <progress
        class="progress w-16 failures flex-item"
        value="0"
        max="100"
      />Failures
    </div>
    <div class="grid w-36 h-6 grid-cols-2 content-start">
      <progress
        class="progress w-16 successes flex-item"
        value="0"
        max="100"
      />Successes
    </div>
  </div>

  <div class="card-side right-side card bg-base-100 text-base-content">
    <label class="label cursor-pointer">
      <input
        type="checkbox"
        class="toggle {toggleStyle}"
        bind:checked={mapBrushToggle}
      />
      <span class="label-text">Map Brush-Out</span>
    </label>
    <label class="label cursor-pointer">
      <input
        type="checkbox"
        class="toggle {toggleStyle}"
        bind:checked={setToggle}
      />
      <span class="label-text">Invert Filters</span>
    </label>
    <label class="label cursor-pointer">
      <input
        type="checkbox"
        class="toggle {toggleStyle}"
        bind:checked={setOffToggle}
      />
      <span class="label-text">Filters Off</span>
    </label>
  </div>

  <div class="left-after-stats">
    <div class="btn-group flex-item">
      <input
        type="radio"
        name="options"
        data-title="S+F"
        bind:group={setGroup}
        class="btn bg-base-100 text-base-content"
        checked
        value="all"
      />
      <input
        type="radio"
        name="options"
        data-title="S"
        bind:group={setGroup}
        class="btn bg-base-100 text-base-content"
        value="out"
      />
      <input
        type="radio"
        name="options"
        data-title="F"
        bind:group={setGroup}
        class="btn bg-base-100 text-base-content"
        value="in"
      />
    </div>
    <div
      class="card cfa-val flex-item bg-base-100 text-base-content mx-auto w-full max-w-xs flex-1 p-8"
    >
      x: {xVal} <br /> y: {yVal} <br /> CFA: {cfaVal}
    </div>

    <div
      class="form-control flex-item card bg-base-100 text-base-content mx-auto w-full max-w-xs flex-1 p-8"
    >
      <!-- <label class="label cursor-pointer">
        <input
          type="checkbox"
          class="toggle {toggleStyle}"
          bind:checked={waypointsToggle}
        />
        <span class="label-text">WPs</span>
      </label> -->
      <label class="label cursor-pointer">
        <input
          type="checkbox"
          class="toggle {toggleStyle}"
          bind:checked={truePathToggle}
        />
        <span class="label-text">True path</span>
      </label>
      <label class="label cursor-pointer">
        <input
          type="checkbox"
          class="toggle {toggleStyle}"
          bind:checked={pathsToggle}
        />
        <span class="label-text">Hexmap</span>
      </label>
      <label class="label cursor-pointer">
        <input
          type="checkbox"
          class="toggle {toggleStyle}"
          bind:checked={rShowToggle}
        />
        <span class="label-text">Tilt</span>
      </label>
      <label class="label cursor-pointer">
        <input
          type="checkbox"
          class="toggle {toggleStyle}"
          bind:checked={pointsToggle}
        />
        <span class="label-text">Points</span>
      </label>
      <label class="label cursor-pointer">
        <input
          type="checkbox"
          class="toggle {toggleStyle}"
          bind:checked={showCFA}
        />
        <span class="label-text">CFA</span>
      </label>
    </div>
  </div>

  <div
    tabindex="0"
    class="right-side collapse collapse-arrow bg-base-100 group"
  >
    <input type="checkbox" class="peer" />
    <div class="collapse-title bg-base-100 text-base-content">
      <svg
        xmlns="http://www.w3.org/2000/svg"
        class="h-5 w-5 icon"
        fill="none"
        viewBox="0 0 24 24"
        stroke="currentColor"
        ><path
          stroke-linecap="round"
          stroke-linejoin="round"
          stroke-width="2"
          d="M9 19v-6a2 2 0 00-2-2H5a2 2 0 00-2 2v6a2 2 0 002 2h2a2 2 0 002-2zm0 0V9a2 2 0 012-2h2a2 2 0 012 2v10m-6 0a2 2 0 002 2h2a2 2 0 002-2m0 0V5a2 2 0 012-2h2a2 2 0 012 2v14a2 2 0 01-2 2h-2a2 2 0 01-2-2z"
        /></svg
      >
      Filter by Summary Metrics
    </div>
    <div
      class="collapse-content stats shadow stats-vertical bg-accent-content text-neutral"
    >
      <!-- <Histogram x="slip" /> -->
      <Histogram x="distance" alias="Slip"/>
      <Histogram x="time" />
      <Histogram x="time" alias="Inefficiency" />
    </div>
  </div>
</main>

<style>
  .left-side {
    left: 30px;
    width: 142px;
    position: fixed;
    top: 20px;
    z-index: 20;
  }

  .stats {
    border-radius: 2px;
  }

  .attrs {
    z-index: 20;
    position: fixed;
    top: 20px;
    left: 40px;
    width: 200px;
  }

  .attrs-ul {
    flex-direction: column;
  }

  .bottom {
    position: fixed;
    top: calc(100vh - 56px);
    z-index: 20;
    right: 30px;
    width: 400px;
    border-radius: 2px;
    padding: 4px 10px;
  }

  .flex-item {
    margin-top: 8px;
  }

  .radial-progress {
    margin: 4px 0px 0px 6px;
  }

  .left-after-stats {
    position: fixed;
    top: 583px;
    width: 143px;
    display: flex;
    flex-direction: column;
    z-index: 20;
    justify-content: center;
    left: 30px;
  }

  .right-side.legend {
    top: 20px;
    right: 482px;
    width: 168px;
    border-radius: 2;
    padding: 6px 12px 6px 12px;
    display: flex;
    flex-direction: column;
  }

  .legend .successes {
    background-color: var(--success-color);
    border-radius: 2px;
  }

  .legend .failures {
    background-color: var(--failure-color);
    border-radius: 2px;
  }

  .card-side {
    position: fixed;
    top: 20px;
    z-index: 20;
    border-radius: 2px;
    padding: 6px;
    height: 40px;
  }

  .btn {
    width: 48px;
    border-radius: 2px;
    border-width: 0;
  }

  .btn-group {
    top: 380px;
    border-radius: 2px;
  }

  .card-side .toggle {
    margin: 0px 6px 0px 0px;
  }

  .right-side {
    right: 30px;
    width: 440px;
    position: fixed;
    z-index: 20;
  }

  .toggle {
    width: 48px;
    height: 12px;
    handle-offset: 1.3rem;
  }

  .form-control {
    border-radius: 2px;
    padding: 6px 12px 6px 12px;
  }

  .cfa-val {
    border-radius: 2px;
    padding: 6px 12px 6px 12px;
  }

  .menu {
    position: fixed;
    right: 10px;
    top: 60px;
    z-index: 10;
    width: 400px;
    height: 400px;
  }

  .collapse {
    z-index: 20;
    border-radius: 2px;
    top: 68px;
  }

  .collapse-title {
    display: flex;
    flex-direction: row;
  }

  .icon {
    margin-right: 8px;
  }
</style>
