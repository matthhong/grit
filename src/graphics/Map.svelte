<script>
  import { setContext, getContext, onMount, afterUpdate } from "svelte";
  import { set, setMode, failuresSetMode, brushSet } from "../store.js";
  import * as d3 from "d3";

  let simIds = getContext("simIds");
  let failures = getContext("failures");

  export let x;
  export let y;
  export let showCFA;
  export let mapBrushToggle;
  export let cfaVal;
  export let xVal;
  export let yVal;
  export let bins;
  export let pathsToggle;
  export let truePathToggle;

  let xScale = getContext("xScale");
  let yScale = getContext("yScale");

  let n;
  let m;

  let simFolder = getContext('simFolder');
  let cfaFile = getContext('cfa');
  let demFile = getContext('dem');

  import { PGMLoaderBase } from "../pgm-loader.js";

  let loader = new PGMLoaderBase();

  async function fetchData() {
    // const cfa = await loader.load("/" + simFolder + "/" + cfaFile + ".pgm");

    // const dem = await loader.load("/" + simFolder + "/" + demFile + ".pgm");
    const cfa = await loader.load("/" + cfaFile + ".pgm");

    const dem = await loader.load("/" + demFile + ".pgm");
    n = cfa.width;
    m = cfa.height;

    return { cfa, dem };
  }

  const height = 600;
  const width = 600;

  let terrainColorScale = d3
    .scaleSequential(d3.interpolateGreys)
    .domain([65525, -28082]);

  let brushes = [];

  let filteredSims = [];

  let el;

  const svg = d3
    .create("svg")
    .attr("preserveAspectRatio", "xMidYMid meet")
    .attr("viewBox", [0, 0, width, height])
    .style("background-color", "hsl(var(--nc))");

  svg.on("mousemove", (ev, d) => {
    xVal = xScale.invert(d3.pointer(ev)[0]).toFixed(1);
    yVal = yScale.invert(d3.pointer(ev)[1]).toFixed(1);
  });

  let terrainMap = svg.append("g");
  let cfaMap = svg.append("g").attr("class", "cfaMap");
  let boundariesMap = svg.append("g");
  let waypointsGroup = svg.append("g");
  let fireworksGroup = svg.append("g");
  let pathGroup = svg.append("g");
  let waypointsReachedGroup = svg.append("g");
  let failureLocsGroup = svg.append("g");
  let xAxisGroup = svg.append("g");
  let yAxisGroup = svg.append("g");
  let brushGroup = svg.append("g");
  let pointsGroup = svg.append("g");

  setContext("pointsGroup", pointsGroup);
  setContext("waypointsGroup", waypointsGroup);
  setContext("pathGroup", pathGroup);

  let startIconGroup = svg.append("g");

  startIconGroup
    .append("image")
    .attr("transform", "rotate(0 45 0)")
    .attr("x", xScale(0) - 10)
    .attr("y", yScale(0) - 10)
    .attr("xlink:href", "rover-yellow.svg")
    .attr("width", 20)
    .attr("height", 20)
    .attr("opacity", 0.8);
  // .on("click", animatePaths);


  // Create a canvas context to draw webgl stuff
  let canvas = document.createElement("canvas");
  let canvas2 = document.createElement("canvas");
  let context = canvas.getContext("2d");
  let context2 = canvas2.getContext("2d");
  let canvasWidth = width * 3;
  let canvasHeight = height * 3;
  canvas.width = canvasWidth;
  canvas.height = canvasHeight;
  canvas2.width = canvasWidth;
  canvas2.height = canvasHeight;

  // Make sure the canvas always fill up 100% of the parent container
  canvas.style.width = "100%";
  canvas.style.height = "auto";
  canvas2.style.width = "100%";
  canvas2.style.height = "auto";



  let history = getContext("history");
  let xAccessor = (d) => d['ROVER_X'];
  let yAccessor = (d) => d['ROVER_Y'];
  

  // function animatePaths() {
    // In the canvas context, draw the paths

    context.strokeStyle = "white";
    context.lineWidth = 1;
    context.globalAlpha = 1;
    context2.strokeStyle = "black";
    context2.lineWidth = 1;
    context2.globalAlpha = 1;

  function drawPath(pathData, transform) {
    context2.save();
    context2.clearRect(0, 0, canvasWidth, canvasHeight);
    context2.translate(transform.x * 3, transform.y * 3);
    context2.scale(transform.k, transform.k);

    context2.beginPath();
    pathData.forEach((d, i) => {
      let x = xScale(xAccessor(d)) * 3;
      let y = yScale(yAccessor(d)) * 3;
      if (i === 0) {
        context2.moveTo(x, y);
      } else {
        context2.lineTo(x, y);
      }
    });

    context2.stroke();
    context2.restore();
  }
  
  function drawPaths(bools, mode, failuresMode, transform){
    context.save();
    context.clearRect(0, 0, canvasWidth, canvasHeight);
    context.translate(transform.x * 3, transform.y * 3);
    context.scale(transform.k, transform.k);

    $history.filter((d, i) => {
      if (mode == 'in' && bools[i]) {
        return true;
      } else if (mode == 'out' && !bools[i]) {
        return true;
      } else if (mode == 'all') {
        return true;
      }
    }).filter((d, i) => {
      if (failuresMode == 'in' && $failures[i]) {
        return true;
      } else if (failuresMode == 'out' && !$failures[i]) {
        return true;
      } else if (failuresMode == 'all') {
        return true;
      }
    }).forEach((d) => {
      let pathData = d['history'];
      // Draw the path for each simulation
      context.beginPath();
      pathData.forEach((d, i) => {
        let x = xScale(xAccessor(d)) * 3;
        let y = yScale(yAccessor(d)) * 3;
        if (i === 0) {
          context.moveTo(x, y);
        } else {
          context.lineTo(x, y);
        }
      });
      context.stroke();
    });
    context.restore();
  }

  let extents = [];

  function newBrush(g) {
    const brush = d3
      .brush()
      .on("start", brushStart)
      .on("brush", brushed)
      .on("end", brushend)
      .extent([
        [0, 0],
        [width, height],
      ]);

    brushes.push({ id: brushes.length, brush: brush });

    function brushStart() {}

    function brushed() {}

    function brushend() {
      let ext = d3.brushSelection(this);
      let brushId = parseInt(this.id.split("-")[1]);

      d3.select(this).call(styleBrush, ext);

      var lastBrushID = brushes[brushes.length - 1].id;
      var lastBrush = document.getElementById("brush-" + lastBrushID);
      var selection = d3.brushSelection(lastBrush);

      if (selection && selection[0] !== selection[1]) {
        newBrush(brushGroup);
        extents.push(ext);
      } else {
        extents[brushId] = ext;
      }

      filteredSims = [];

      bins.map((bin) => {
        extents.map((v) => {
          if (
            ((bin.x >= v[0][0] && bin.x <= v[1][0]) ||
              (bin.x <= v[0][0] && bin.x >= v[1][0])) &&
            ((bin.y >= v[0][1] && bin.y <= v[1][1]) ||
              (bin.y <= v[0][1] && bin.y >= v[1][1]))
          ) {
            filteredSims.push(...bin.map((sim) => sim.simId));
          }
        });
      });
      filteredSims = Array.from(new Set(filteredSims));
      brushSet.set($simIds.map((simId) => filteredSims.includes(simId)));

      drawBrushes(brushGroup);
    }
  }

  function styleBrush(g, ext) {
    let center = [ext[0][0] + ext[1][0] / 2, ext[0][1] + ext[1][1] / 2];
    g.select("text").remove();
    g.append("text")
      .text(
        "cx: " +
          center[0].toFixed(2) +
          ", " +
          "cy: " +
          center[1].toFixed(2) +
          ", " +
          "w: " +
          Math.abs(ext[0][0] - ext[1][0]).toFixed(2) +
          ", " +
          "h: " +
          Math.abs(ext[0][1] - ext[1][1]).toFixed(2)
      )
      .attr("font-size", 6)
      .attr("fill", "black")
      .attr("x", ext[0][0])
      .attr("y", ext[0][1] - 4);
  }

  function drawBrushes(g) {
    var brushSelection = g.selectAll(".brush").data(brushes, function (d) {
      return d.id;
    });

    brushSelection
      .enter()
      .insert("g", ".brush")
      .attr("class", "brush")
      .attr("id", function (brush) {
        return "brush-" + brush.id;
      })
      .each(function (brushObject) {
        d3.select(this).call(brushObject.brush);
      });

    brushSelection.each(function (brushObject) {
      d3.select(this)
        .attr("class", "brush")
        .selectAll(".overlay")
        .style("pointer-events", function () {
          var brush = brushObject.brush;
          if (brushObject.id === brushes.length - 1 && brush !== undefined) {
            return "all";
          } else {
            return "none";
          }
        });
    });

    brushSelection.exit().remove();
  }

  function adjustXTickLabels(selection) {
    selection
      .selectAll(".tick text")
      .attr("font-size", "0.6em")
      .attr("fill", "hsl(var(--n))")
      .attr("transform", "translate(-2,-7)")
      .attr("text-anchor", "end");

    selection.selectAll(".tick line").attr("stroke", "hsl(var(--n))");
  }

  function adjustYTickLabels(selection) {
    selection
      .selectAll(".tick text")
      .attr("font-size", "0.6em")
      .attr("fill", "hsl(var(--n))")
      .attr("transform", "translate(-8,-4)")
      .attr("text-anchor", "start");

    selection.selectAll(".tick line").attr("stroke", "hsl(var(--n))");
  }

  function xAxis(g, x) {
    g.attr("transform", `translate(0,0)`)
      .call(d3.axisBottom(x).ticks(8))
      .call(adjustXTickLabels);
  }

  function yAxis(g, y) {
    g.call(d3.axisRight(y).ticks(8 * (height / width))).call(adjustYTickLabels);
  }

  $: {
    if (!pathsToggle) {
      // Hide canvas  
      canvas.style.display = "none";
    } else {
      // Show canvas
      canvas.style.display = "block";
    }
  }

  $: {
    if (!truePathToggle) {
      // Hide canvas  
      canvas2.style.display = "none";
    } else {
      // Show canvas
      canvas2.style.display = "block";
    }
  }

  $: {
    if (!mapBrushToggle) {
      svg
        .call(zoom)
        .call(
          zoom.transform,
          d3.zoomIdentity
            .translate(currentTransform.x, currentTransform.y)
            .scale(currentTransform.k)
        )
        .on("dblclick.zoom", null);
      brushGroup.style("display", "none");
    } else {
      newBrush(brushGroup);
      drawBrushes(brushGroup);

      svg.on(".zoom", null);
      brushGroup.style("display", "block");
    }
  }

  const zoom = d3.zoom().scaleExtent([0.8, 10]).on("zoom", zoomed);

  let currentTransform = {};

  svg
    .call(zoom)
    .call(zoom.transform, d3.zoomIdentity)
    .on("dblclick.zoom", null);

  // Zoom into canvas context
  d3.select(context.canvas).call(zoom);
  d3.select(context2.canvas).call(zoom);

  function zoomed({ transform }) {
    currentTransform = transform;
    const zx = transform.rescaleX(xScale).interpolate(d3.interpolateRound);
    const zy = transform.rescaleY(yScale).interpolate(d3.interpolateRound);

    pathGroup
      .attr("transform", transform)
      .attr("stroke-width", 1 / transform.k);
    terrainMap.attr("transform", transform);
    boundariesMap.attr("transform", transform);
    cfaMap.attr("transform", transform);
    waypointsGroup.attr("transform", transform);
    waypointsReachedGroup.attr("transform", transform);
    failureLocsGroup.attr("transform", transform);
    fireworksGroup.attr("transform", transform);
    brushGroup.attr("transform", transform);
    pointsGroup.attr("transform", transform);

    xAxisGroup.call(xAxis, zx);
    yAxisGroup.call(yAxis, zy);
    startIconGroup
      .attr("transform", transform)
      .attr("font-size", 20 / transform.k);

    // context.save();
    // context.clearRect(0, 0, canvasWidth, canvasHeight);
    // context.translate(transform.x * 3, transform.y * 3);
    // context.scale(transform.k, transform.k);
    drawPaths($set, $setMode, $failuresSetMode, currentTransform);
    drawPath($history[0].history, currentTransform);
    // context.restore()
  }

  failuresSetMode.subscribe((v) => {
    drawPaths($set, $setMode, v, currentTransform);
    // filterByFailures(v);
  });

  set.subscribe((v) => {
    drawPaths(v, $setMode, $failuresSetMode, currentTransform);
    // filterByFailures($failuresSetMode);
  });

  setMode.subscribe((v) => {
    drawPaths($set, v, $failuresSetMode, currentTransform);
    // filterByFailures($failuresSetMode);
  });

  onMount(() => {
    fetchData().then((pgms) => {
      terrain(
        terrainMap,
        pgms.dem,
        (d) => terrainColorScale(d.value),
        "dem",
        false,
        2000
      );
      cfaTextureMap(pgms.cfa);
      terrain(boundariesMap, pgms.dem, "none", "boundaries", true, 8000);

      let canvasPlot = document.getElementById("scatterplot");
      canvasPlot.appendChild(context.canvas);

      let canvasPlot2 = document.getElementById("scatterplot2");
      canvasPlot2.appendChild(context2.canvas);

      el.append(svg.node());

      toggleCFA();
    });
  });

  function terrain(group, dem, fill, className, stroke, frequency) {
    let contours = group
      .selectAll("path." + className)
      .data(
        d3
          .contours()
          .size([dem.width, dem.height])
          .thresholds(d3.range(0, 65525, frequency))(dem.data)
      )
      .enter()
      .append("path");

    contours.attr("class", className);

    if (stroke) {
      contours
        .attr("stroke", "#777777")
        .attr("stroke-width", 0.2)
        .attr("stroke-opacity", 1);
    }
    contours
      .attr("d", d3.geoPath(d3.geoIdentity().scale(width / dem.width)))
      .attr("fill", fill)
      .attr("opacity", 1);
  }

  function cfaTextureMap(cfa) {
    let xBoundaries = [];
    let yBoundaries = [];

    let prevRow = [];
    for (var j = 0, k = 0, l = 0; j < m; ++j) {
      var currentRow = [];
      var prevCell = -1;
      for (var i = 0; i < n; ++i, ++k, l += 4) {
        currentRow.push(cfa.data[k]);

        if (cfa.data[k] != prevCell) {
          xBoundaries.push(i);
        }
        prevCell = cfa.data[k];
      }
      if (JSON.stringify(currentRow) !== JSON.stringify(prevRow)) {
        yBoundaries.push(j);
      }
      prevRow = currentRow;
    }

    xBoundaries = [...new Set(xBoundaries)].sort(function (a, b) {
      return a - b;
    });
    yBoundaries = [...new Set(yBoundaries)].sort(function (a, b) {
      return a - b;
    });

    const cfaMat = cfa.data.reduce(
      (rows, key, index) =>
        (index % n == 0
          ? rows.push([key])
          : rows[rows.length - 1].push(key)) && rows,
      []
    );

    let cfaColorScale = d3
      .scaleSequential(d3.interpolateGreys)
      // .domain(d3.extent(cfa.data));
      .domain([0, 1666]);
    

    let cfaXScale = d3
    .scaleLinear()
    .domain([0, n])
    .nice()
    .range([0, width]);

    xBoundaries.map((xBound, i) => {
      yBoundaries.map((yBound, j) => {
        cfaMap
          .append("rect")
          .datum(cfaMat[yBound][xBound])
          .attr("class", "cfa")
          .attr("x", xBound / 2)
          .attr("y", yBound / 2)
          .attr("height", () => {
            if (j + 1 >= yBoundaries.length) {
              return (m - yBound) / 2;
            } else {
              return (yBoundaries[j + 1] - yBound) / 2;
            }
          })
          .attr("width", () => {
            if (i + 1 >= xBoundaries.length) {
              return (m - xBound) / 2;
            } else {
              return (xBoundaries[i + 1] - xBound) / 2;
            }
          })
          .attr("fill", (d) => cfaColorScale(d))
          .attr("opacity", 1)
          .on("mouseover", (ev, d) => {
            cfaVal = d / 1000;
          });

        cfaMap
          .append("text")
          .attr("class", "cfa")
          .attr("font-size", "0.6em")
          .attr("x", xBound / 2 + 3)
          .attr("y", yBound / 2 + 12)
          .text(cfaMat[yBound][xBound] / 1000);
      });
    });
  }

  function toggleCFA() {
    if (showCFA) {
      d3.selectAll("path.dem").attr("opacity", 0);
      d3.selectAll("path.boundaries").attr("opacity", 1);
      d3.selectAll("g.cfaMap").attr("opacity", 1);
    } else {
      d3.selectAll("path.dem").attr("opacity", 1);
      d3.selectAll("path.boundaries").attr("opacity", 0);
      d3.selectAll("g.cfaMap").attr("opacity", 0);
    }
  }

  $: {
    showCFA;
    toggleCFA();
  }
</script>

<div style="position: relative;">
  <div id="scatterplot" class="canvas-plot" />
  <div id="scatterplot2" class="canvas-plot" />
  <div bind:this={el} id="map" class="plot" />
  <slot />
  <div id="tooltip" />
</div>

<style>
  .plot {
    position: absolute;
    top: 0;
    left: 0;
    width: 100vw;
    height: 100vh;
    cursor: pointer;
    overflow: hidden;
  }

  .canvas-plot {
    z-index: 2;
    position: absolute;
    width: 100vw;
    height: 100vh;
    pointer-events: none;
  }

  #map {
    z-index: 1;
  }

  canvas {
    position: relative;
    width: 100%;
  }

  #tooltip {
    position: fixed;
    display: none;
    padding: 3px 6px;
    background: hsl(var(--b1));
    opacity: 0.7;
    color: white;
    border-radius: 2;
    pointer-events: none;
    z-index: 100;
  }
</style>
