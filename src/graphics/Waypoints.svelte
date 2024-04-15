<script>
  import { getContext, onMount } from "svelte";

  let xScale = getContext("xScale");
  let yScale = getContext("yScale");
  let rScale = getContext("rScale");

  let svgGroup = getContext("waypointsGroup");
  export let show;

  let waypoints = getContext("waypoints");

  let goalColor = "hsl(var(--wa))";
  let wpColor = "hsl(var(--wa))";

  let wpOpacity = 0.5;

  svgGroup
    .append("image")
    .attr("transform", "rotate(0 45 0)")
    .attr("x", xScale(0) - 10)
    .attr("y", yScale(0) - 10)
    .attr("xlink:href", "rover-yellow.svg")
    .attr("width", 20)
    .attr("height", 20)
    .attr("opacity", 0.8);
  // .on("click", animatePaths)

  function drawWayPoints() {
    let n = $waypoints.length;
    svgGroup
      .selectAll("circle.wp")
      .data($waypoints)
      .enter()
      .append("circle")
      .attr("class", "wp")
      .attr("cx", (d) => xScale(d.cx))
      .attr("cy", (d) => yScale(d.cy))
      .attr("r", (d) => rScale(d.r))
      .attr("stroke-width", 2)
      .attr("stroke", (d, i) => {
        if (i == n - 1) {
          return goalColor;
        }
        return wpColor;
      })
      .attr("stroke-opacity", 0.5)
      .attr("fill", "none");

    svgGroup

      .append("image")
      .datum($waypoints.slice($waypoints.length - 1)[0])
      .attr("width", 20)
      .attr("x", (d) => xScale(d.cx) - 6)
      .attr("y", (d) => yScale(d.cy) - 16)
      .attr("xlink:href", "checkered-flag-01.svg")
      .attr("opacity", 1);

    svgGroup
      .selectAll("text.wp")
      .data($waypoints.slice(0, $waypoints.length - 1))
      .enter()
      .append("text")
      .attr("class", "wp")
      .attr("x", (d) => xScale(d.cx) - 4)
      .attr("y", (d) => yScale(d.cy) - rScale(d.r) + 14)
      .text((d, i) => i + 1)
      .attr("font-size", "0.8em")
      .attr("font-family", "Cairo")

      .attr("fill", (d, i) => {
        if (i == n - 1) {
          return goalColor;
        }
        return wpColor;
      })
      .attr("fill-opacity", wpOpacity);
  }

  function toggleWaypoints(v) {
    if (v) {
      svgGroup.attr("opacity", 1);
    } else {
      svgGroup.attr("opacity", 0);
    }
  }

  $: {
    toggleWaypoints(show);
  }

  onMount(() => {
    drawWayPoints();
  });
</script>
