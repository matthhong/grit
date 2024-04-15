<script>
  import { getContext, onMount } from "svelte";
  import { setMode, set, failuresSetMode } from "../store.js";
  import Tooltip from "../lib/Tooltip.js";
  import * as d3 from "d3";

  let svgGroup = getContext("pathGroup");
  export let threshold;
  export let show;
  export let rShow;
  export let bins;
  export let emptyBins;

  let failures = getContext("failures");
  let simIds = getContext("simIds");
  let history = getContext("history");
  let hexbin = getContext("hexbin");

  let hexColorScale = d3
    .scaleOrdinal(getContext("colormap"))
    .domain([0, 0.33, 0.5, 0.66, 1])

  let hexValMap = function(v) {
    return 0.5;
  }
  
  window.colorScale = hexColorScale;
  window.d3 = d3

  function drawHexes() {
    let hist = bins.map((bin, i) => {
      let failuresHere = bin.filter(
        (d) => $failures[$simIds.indexOf(d.simId)]
      ).length;
      return {
        len: emptyBins[i].length,
        x: bin.x,
        y: bin.y,
        failures: failuresHere,
      };
    });

    let highTimeData = bins.map((bin, i) => {
      return {
        len: bin.filter((v) => v.r > threshold).length,
        x: bin.x,
        y: bin.y,
      };
    });

    let rScale = d3
      .scaleSqrt()
      .domain([0, d3.max(hist, (d) => d.len)])
      .range([0, hexbin.radius()]);

    let rTimeScale = d3
      .scaleSqrt()
      .domain([0, d3.max(highTimeData, (d) => d.len)])
      .range([0, hexbin.radius()]);

    if (!rShow) {
      svgGroup
        .selectAll("path.hex")
        .data(hist)
        .join("path")
        .attr("class", "hex")
        .attr("d", (d) => hexbin.hexagon(rScale(d.len)))
        // .attr("fill", (d) => hexColorScale(d.failures / d.len))
        .attr("fill", (d) => {
          // console.log(d.failures / d.len);
          // console.log(hexBandScale.step());
          // return hexBandScale.invert(d.failures / d.len)
          return hexColorScale(hexValMap(d.failures / d.len))
        })
        .attr("transform", (d) => `translate(${d.x},${d.y})`)
        
    } else {
      svgGroup
        .selectAll("path.hex")
        .data(highTimeData)
        .join("path")
        .attr("class", "hex")
        .attr("d", (d) => hexbin.hexagon(rTimeScale(d.len)))
        .attr("transform", (d) => `translate(${d.x},${d.y})`)
        .attr("fill", (d) => "#2A303C")
        .attr("fill-opacity", 1);
    }
  }

  let tooltip;
  let xScale = getContext("xScale");
  let yScale = getContext("yScale");

  function isPointInHexagon(point, center, radius) {
    var cx = center[0];
    var cy = center[1];
    var px = point[0];
    var py = point[1];
    
    // Calculate the distance between the center and the point
    var distance = Math.sqrt(Math.pow(px - cx, 2) + Math.pow(py - cy, 2));
    
    // Check if the distance is less than or equal to the radius
    if (distance <= radius) {
      // Calculate the angle between the center and the point
      var angle = Math.atan2(py - cy, px - cx);
      
      // Convert the angle to degrees
      angle = (angle * 180 / Math.PI + 360) % 360;
      
      // Check if the point lies within the hexagon's angles
      if (angle >= 60 && angle <= 300) {
        return true;
      }
    }
    
    return false;
  }

  function isPathInHexagon(path, center, radius) {
    // Iterate over each point in the path
    for (var i = 0; i < path.length; i++) {
      var point = [xScale(path[i]['ROVER_X']), yScale(path[i]['ROVER_Y'])];

      // Check if the current point falls inside the hexagon
      if (isPointInHexagon(point, center, radius)) {
        return true;
      }
    }

    return false;
  }

  function createTooltip() {

    function tooltipContents(datum) {
      let center = [datum.x, datum.y];
      let rad = hexbin.radius();

      let inObstacle = []

      // For every point in history, check if it is in the hexagon
      $history.forEach((h, i) => {
        let path = h.history;

        if (isPathInHexagon(path, center, rad)) {
          inObstacle.push(i);
        }
      });

      return `  ${100 * inObstacle.length / $simIds.length}%`;
    }

    svgGroup
      .selectAll("path.hex")
      .on("mouseover", (event, d) => {
        tooltip.display(d, tooltipContents);
        d3.select(event.target).attr("stroke", "black");
        // drawPath($history[d.simIndex].history, d.simIndex)
      })
      .on("mouseout", (event, d) => {
        tooltip.hide();
        d3.select(event.target).attr("stroke", "none");
        // if (!highlight.includes(d.simIndex)) {
        //   d3.selectAll("path.line.sim" + d.simIndex).remove();
        // }
      })
      .on("mousemove", (event) => {
        tooltip.move(event);
      })

  }


  function toggle(v) {
    if (v) {
      svgGroup.attr("opacity", 1);
    } else {
      svgGroup.attr("opacity", 0);
    }
  }

  failuresSetMode.subscribe((v) => {
    drawHexes();
  });

  set.subscribe((v) => {
    drawHexes();
  });

  setMode.subscribe((v) => {
    drawHexes();
  });

  $: {
    toggle(show);
  }

  $: {
    rShow;
    bins;
    drawHexes();
  }

  onMount(() => {
    tooltip = new Tooltip(d3.select("#tooltip"));
    drawHexes();

    createTooltip();
  });
</script>
