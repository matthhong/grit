<script>
  import { onMount, getContext } from "svelte";
  import Tooltip from "../lib/Tooltip.js";
  import * as d3 from "d3";
  import { setMode, failuresSetMode, set } from "../store.js";

  let svgGroup = getContext("pointsGroup");
  let history = getContext("history");
  let failures = getContext("failures");
  let simIds = getContext("simIds");

  let xAccessor = (d) => d['ROVER_X'];
  let yAccessor = (d) => d['ROVER_Y'];

  let xScale = getContext("xScale");
  let yScale = getContext("yScale");

  export let show;

  let wpReachedRadius = 2;
  // let wpReachedColor = "hsl(var(--wa))";
  let wpReachedColor = getContext("successColor");
  let fillOpacity = 0.6;
  let failureColor = getContext("failureColor");
  let successColor = getContext("successColor");
  let opacity = getContext("pathOpacity")

  let reachedGroup = svgGroup.append("g");
  let failedGroup = svgGroup.append("g");
  let lineGroup = svgGroup.append("g");
  let voronoiGroup = svgGroup.append("g").attr("class", "voronoi");

  let highlight = [];
  let tooltip;

  function createTooltip() {

    function tooltipContents(datum) {
      const { cx, cy, simIndex } = datum;
      return `sim: ${$simIds[simIndex]}, x: ${cx.toFixed(2)}, y: ${cy.toFixed(
        2
      )}`;
    }

    reachedGroup
      .selectAll("circle")
      .on("click", (event, d) => {
        drawPath($history[d.simIndex].history, d.simIndex)
        highlight.push(d.simIndex)
      })
      .on("mouseover", (event, d) => {
        tooltip.display(d, tooltipContents);
        drawPath($history[d.simIndex].history, d.simIndex)
      })
      .on("mouseout", (event, d) => {
        tooltip.hide();
        if (!highlight.includes(d.simIndex)) {
          d3.selectAll("path.line.sim" + d.simIndex).remove();
        }
      })
      .on("mousemove", (event) => {
        tooltip.move(event);
      })

    failedGroup
      .selectAll("circle")
      .on("click", (event, d) => {
        drawPath($history[d.simIndex].history, d.simIndex)
        highlight.push(d.simIndex)
      })
      .on("mouseover", (event, d) => {
        tooltip.display(d, (datum) => {
          const { cx, cy, simIndex } = datum;
          return `sim: ${$simIds[datum.simIndex]}, x: ${datum['ROVER_X'].toFixed(
            2
          )}, y: ${datum['ROVER_Y'].toFixed(2)}`;
        });
        drawPath($history[d.simIndex].history, d.simIndex)
      })
      .on("mouseout", (event, d) => {
        tooltip.hide();
        if (!highlight.includes(d.simIndex)) {
          d3.selectAll("path.line.sim" + d.simIndex).remove();
        }
      })
      .on("mousemove", (event) => {
        tooltip.move(event);
      });
  }

  function drawReached(wpHistory, i) {
    wpHistory.map((v) => {
      if (v.cx) {
        reachedGroup
          .append("circle")
          .datum(() => {
            v.simIndex = i;
            return v;
          })
          .attr("class", "wp-reached sim" + i)
          .attr("cx", (d) => xScale(d.cx))
          .attr("cy", (d) => yScale(d.cy))
          .attr("fill", wpReachedColor)
          .attr("fill-opacity", fillOpacity)
          .attr("r", () => {
            return wpReachedRadius;
          });
      }
    });
  }

  function drawFailed(v, i) {
    // console.log(i);
    failedGroup
      .append("circle")
      .datum(() => {
        v.simIndex = i;
        return v;
      })
      .attr("class", "failed sim" + i)
      .attr("cx", (d) => xScale(xAccessor(d)))
      .attr("cy", (d) => yScale(yAccessor(d)))
      .attr("fill", failureColor)
      .attr("fill-opacity", fillOpacity)
      .attr("r", 4);
  }

  function filterRoverPaths(bools, mode) {
    bools.map((v, i) => {
      if (mode == "in") {
        if (v) {
          //   d3.selectAll("path.line.sim" + i).attr("stroke-opacity", 0.4);
          d3.selectAll("circle.wp-reached.sim" + i).attr("fill-opacity", 0.5);
          d3.selectAll("circle.failed.sim" + i).attr("fill-opacity", 0.5);
        } else {
          //   d3.selectAll("path.line.sim" + i).attr("stroke-opacity", 0);
          d3.selectAll("circle.wp-reached.sim" + i).attr("fill-opacity", 0);
          d3.selectAll("circle.failed.sim" + i).attr("fill-opacity", 0);
        }
      } else if (mode == "out") {
        if (v) {
          //   d3.selectAll("path.line.sim" + i).attr("stroke-opacity", 0);
          d3.selectAll("circle.wp-reached.sim" + i).attr("fill-opacity", 0);
          d3.selectAll("circle.failed.sim" + i).attr("fill-opacity", 0);
        } else {
          //   d3.selectAll("path.line.sim" + i).attr("stroke-opacity", 0.4);
          d3.selectAll("circle.wp-reached.sim" + i).attr("fill-opacity", 0.5);
          d3.selectAll("circle.failed.sim" + i).attr("fill-opacity", 0.5);
        }
      } else {
        // d3.selectAll("path.line.sim" + i).attr("stroke-opacity", 0.4);
        d3.selectAll("circle.wp-reached.sim" + i).attr("fill-opacity", 0.5);
        d3.selectAll("circle.failed.sim" + i).attr("fill-opacity", 0.5);
      }
    });
  }

  function filterByFailures(mode) {
    if (mode == "in") {
      $failures.map((v, i) => {
        if (!v) {
          // d3.selectAll("path.line.sim" + i).attr("stroke-opacity", 0);
          d3.selectAll("circle.wp-reached.sim" + i).attr("fill-opacity", 0);
          d3.selectAll("circle.failed.sim" + i).attr("fill-opacity", 0);
        }
      });
    } else if (mode == "out") {
      $failures.map((v, i) => {
        if (v) {
          // d3.selectAll("path.line.sim" + i).attr("stroke-opacity", 0);
          d3.selectAll("circle.wp-reached.sim" + i).attr("fill-opacity", 0);
          d3.selectAll("circle.failed.sim" + i).attr("fill-opacity", 0);
        }
      });
    }
  }

  function drawDelauney(bools, mode, failuresSetMode) {
    d3.selectAll("path.voronoi").remove();
    let allPoints = [];
    // let simIds = [];
    // Get all points in wpHistory and failed 
    $history.map((datum, i) => {
      if (mode == "in") {
        if (!bools[i]) {
          return;
        }
      } else if (mode == "out") {
        if (bools[i]) {
          return;
        }
      }
      if (failuresSetMode == "in") {
        if (!$failures[i]) {
          return;
        }
      } else if (failuresSetMode == "out") {
        if ($failures[i]) {
          return;
        }
      }

      let wpHistory = datum['wpHistory'];
      wpHistory.map((v) => {
        if (v.cx) {
          allPoints.push([xScale(v.cx), yScale(v.cy), datum["simId"]]);
        }
      });

      let failed = datum["history"][datum["history"].length - 1];
      allPoints.push([xScale(xAccessor(failed)), yScale(yAccessor(failed)), datum["simId"]]);
      // simIds = [...simIds, i];
    });

    var delaunay = d3.Delaunay.from(allPoints.map((d) => d.slice(0, 2)));
    var voronoi = delaunay.voronoi([0, 0, 600, 600]);


    // Draw the voronoi tessellation
    let popover = (g, value) => {
      if (!value) return g.style("display", "none");

      // tooltip group
      g
        .style("display", null)
        .style("pointer-events", "none")
        .style("font", "6px sans-serif");

      // tooltip container stroke
      const path = g.selectAll("path")
        .data([null])
        .join("path")
          .attr("fill", "white")
          .attr("fill-opacity", 0.6)
          // .attr("stroke", "black");

      // tooltip content
      const text = g.selectAll("text")
        .data([null])
        .join("text")
        .call(text => text
          .selectAll("tspan")
          .data((value + "").split(/\n/))
          .join("tspan")
            .attr("x", 0)
            .attr("y", (d, i) => `${i * 1.1}em`)
            .style("text-align", "center")
            .style("font-weight", (_, i) => i ? null : "bold")
            .text(d => d));

      // tooltip positioning
      const {x, y, width: w, height: h} = text.node().getBBox();
      text.attr("transform", `translate(${-w / 2},${7 - y})`);
      
      // tooltip container path
      path.attr("d", `M${-w / 2 - 4},5H${w / 2 + 4}v${h + 5}h-${w + 8}z`);
    }

      voronoiGroup
        .selectAll("path")
        .data(allPoints)
        .enter()
        .append("path")
        .attr("d", (d, i) => {
          return voronoi.renderCell(i);
        })
        .attr("fill", "none")
        .attr("stroke", "none")
        // .attr("stroke", "black")
        // .attr("stroke-opacity", 1)
        // .attr("stroke-width", 0.5)
        .attr("pointer-events", "all")
        .attr("class", (d, i) => {
          return "voronoi sim" + i;
        })
        .on("mouseover", (event, d) => {
          // if (d.y > 1) {
            // console.log(d);
            d3.selectAll("circle.wp-reached")
              .attr("stroke", "none")
              d3.selectAll("circle.failed")
              .attr("stroke", "none")

            svgGroup.selectAll('.tooltip').remove()

            let simIndex = $history.findIndex((datum) => datum["simId"] == d[2]);

            d3.selectAll("circle.wp-reached.sim" + simIndex)
                .attr("stroke", "white")
                .attr("stroke-width", 1)
              d3.selectAll("circle.failed.sim" + simIndex)
                .attr("stroke", "white")
                .attr("stroke-width", 1)

            svgGroup.append('g')
              .attr("class", "tooltip")
              .attr("transform", `translate(${d[0]}, ${d[1]})`)
              .call(popover, `sim: ${d[2]}`)
              d3.selectAll("path.line").remove();
          drawPath($history[simIndex].history, simIndex)
          // }
        })
  }



  function drawPath(pathData, simIndex) {
    var pathGenerator = d3
      .line()
      .curve(d3.curveCatmullRom)
      .x((d) => xScale(xAccessor(d)))
      .y((d) => yScale(yAccessor(d)));

    let path = lineGroup
      .append("path");

    path.datum(pathData)
      .attr("class", "line sim" + simIndex)
      .attr("fill", "none")
      .attr("stroke", (d, i) => {
        if ($failures[simIndex]) {
          return failureColor;
        } else {
          return successColor;
        }
      })
      .attr("stroke-opacity", opacity)
      .attr("stroke-linejoin", "round")
      .attr("stroke-linecap", "round")
      .attr("d", (d) => {
        return pathGenerator(d).replace(/(\.\d{1})\d+/g, "$1");
      })
    
      path.on("click", (event, d) => {
        var index = highlight.indexOf(simIndex);
        if (index > -1) {
          highlight.splice(index, 1);
        }
        d3.selectAll("path.line.sim" + simIndex).remove();
      })
      .on("mouseover", (event, d) => {
        tooltip.display(d, (datum) => {
          return `sim: ${$simIds[simIndex]}`
        });
      })
      .on("mouseout", (event, d) => {
        tooltip.hide();
      })
      .on("mousemove", (event) => {
        tooltip.move(event);
      });
  }

  function toggle(v) {
    if (v) {
      svgGroup.attr("display", "block");
    } else {
      if (tooltip) {
        tooltip.hide();
      }
      // tooltip.hide();
      svgGroup.attr("display", "none");
    }
  }

  $: {
    toggle(show);
  }

  failuresSetMode.subscribe((v) => {
    filterRoverPaths($set, $setMode);
    filterByFailures(v);
    drawDelauney($set, $setMode, v);
  });

  set.subscribe((v) => {
    filterRoverPaths(v, $setMode);
    filterByFailures($failuresSetMode);
    drawDelauney(v, $setMode, $failuresSetMode);
  });

  setMode.subscribe((v) => {
    filterRoverPaths($set, v);
    filterByFailures($failuresSetMode);
    drawDelauney($set, v, $failuresSetMode);
  });

  onMount(() => {
    tooltip = new Tooltip(d3.select("#tooltip"));

    drawDelauney($set, $setMode, $failuresSetMode);

    $history.map((datum, i) => {
      drawReached(datum["wpHistory"], i);

      if ($failures[i]) {
        drawFailed(datum["history"][datum["history"].length - 1], i);
      }
    });

    // createTooltip();
  });
</script>
