<script>
  import * as d3 from "d3";
  import { onMount, getContext } from "svelte";
  import { histogramSets, set } from "../store.js";

  let summary = getContext("summary");
  let simIds = getContext("simIds");

  export let x;
  export let alias = ''

  let el;

  let fillOpacity = 0.8;

  let w = 600;
  let h = 160;

  let margin = {
    top: 10,
    bottom: 45,
    left: 40,
    right: 14,
  };

  let svg = d3
    .create("svg")
    .attr("preserveAspectRatio", "xMidYMid meet")
    .attr("viewBox", "0 0 " + w + " " + h);

  let g = svg
    .append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

  let filteredGroup = svg
    .append("g")
    .attr("transform", `translate(${margin.left}, ${margin.top})`);

  var histogram = d3
    .bin()

    .thresholds(20)
    .value(function (d) {
      return d[x];
    });

  console.log($summary);

  var bins = histogram($summary);

  let binData = {};
  bins.map((v, i) => {
    binData[i] = v.length;
  });

  const [min, max] = d3.extent(Object.keys(binData).map((d) => +d));
  const range = [min, max + 1];

  const width = w - margin.left - margin.right;
  const height = h - margin.top - margin.bottom;

  const xScale = d3.scaleLinear().domain(range).range([0, width]);
  const yScale = d3
    .scaleLinear()
    .domain([0, d3.max(Object.values(binData))])
    .range([height, 0]);

  let binValues = {};
  bins.map((v, i) => {
    binValues[i] = v.map((v) => v);
  });

  let selectedSims = [];

  $: (() =>
    selectedSims.length &&
    histogramSets.update((sets) => {
      let bools = $simIds.map((id) => selectedSims.includes(id));
      sets[x] = bools;
      return sets;
    }))();

  let colorHist = d3
    .scaleOrdinal([getContext("successColor"), getContext("failureColor")])
    .domain(["successes", "failures"]);

  set.subscribe((v) => {
    let filteredBinData = [];

    bins.map((binV, i) => {
      let successCount = 0;
      let failureCount = 0;
      binV.map((sim) => {
        if (v[$simIds.indexOf(sim.simId)] && sim.failure) {
          failureCount++;
        } else if (v[$simIds.indexOf(sim.simId)] && !sim.failure) {
          successCount++;
        }
      });
      filteredBinData.push({
        x: i,
        successes: successCount,
        failures: failureCount,
        total: successCount + failureCount,
      });
    });

    let stack = d3.stack().keys(["successes", "failures"]);

    filteredGroup
      .selectAll("g")
      .data(stack(filteredBinData))

      .join("g")
      .attr("fill", (d) => colorHist(d.key))
      .selectAll("rect.filtered")
      .data((d) => d)

      .join("rect")
      .attr("class", "filtered")

      .attr("fill-opacity", fillOpacity)
      .attr("x", (d) => xScale(d.data.x))
      .attr("y", (d) => yScale(d[1]))
      .attr("width", width / (range[1] - range[0]))
      .attr("height", (d) => yScale(d[0]) - yScale(d[1]));
  });

  function histogramSlider(customOptions) {
    const defaultOptions = {
      w: 600,
      h: 400,
      bucketSize: 1,
      defaultRange: [0, 100],
      format: d3.format(".3s"),
    };

    const { w, h, defaultRange, bucketSize, format } = {
      ...defaultOptions,
      ...customOptions,
    };

    // Print data
    console.log("binData", binData);

    g.append("g")
      .selectAll("rect")
      .data(d3.range(range[0], range[1] + 1))
      .enter()
      .append("rect")
      .attr("x", (d) => xScale(d))
      .attr("y", (d) => yScale(binData[d]))
      .attr("width", width / (range[1] - range[0]))
      .attr("height", (d) => yScale(0) - yScale(binData[d]))
      .style("fill", "white")
      .style("stroke", "gray")
      .style("stroke-width", 1);

    g.append("g")
      .selectAll("line")
      .data(d3.range(range[0], range[1] + 1))
      .enter()
      .append("line")
      .attr("x1", (d) => xScale(d))
      .attr("x2", (d) => xScale(d))
      .attr("y1", 0)
      .attr("y2", height)
      .style("stroke", "#ccc");

    var labelMax = g
      .append("text")
      .attr("id", "label-min")
      .attr("x", "-0.6em")
      .attr("y", height)
      .text(0);

    var labelMax = g
      .append("text")
      .attr("id", "label-max")
      .attr("x", "-0.6em")
      .attr("y", 0)
      .text(d3.max(Object.values(binData)));

    let xLabel = g
      .append("text")
      .attr(
        "transform",
        "translate(" + width / 2 + " ," + (height + margin.top + 30) + ")"
      )
      .style("text-anchor", "middle")
      .style("font-size", 20)
      .style("color", "hsl(var(--nc))")
      .text(alias.charAt(0).toUpperCase() + alias.slice(1) || x.charAt(0).toUpperCase() + x.slice(1));

    let yLabel = g
      .append("text")
      .attr("transform", "rotate(-90)")
      .attr("y", 0 - margin.left)
      .attr("x", 0 - height / 2)
      .attr("dy", "1em")
      .style("text-anchor", "middle")
      .attr("font-size", 20)
      .style("color", "hsl(var(--nc))")
      .text("Count");

    var labelL = g
      .append("text")
      .attr("id", "labelleft")
      .style("text-anchor", "start")
      .attr("x", 0)
      .attr("y", height + 10);

    var labelR = g
      .append("text")
      .attr("id", "labelright")
      .style("text-anchor", "end")
      .attr("x", 0)
      .attr("y", height + 10);

    var brush = d3
      .brushX()
      .extent([
        [0, 0],
        [width, height],
      ])
      .on("brush", function ({ selection }) {
        var s = selection;

        labelL
          .attr("x", s[0])
          .text(
            (bins[parseInt(xScale.invert(s[0]))].x0 * bucketSize).toFixed(2)
          );
        labelR.attr("x", s[1]).text(() => {
          return xScale.invert(s[1]) == bins.length
            ? (bins[max].x0 * bucketSize).toFixed(2)
            : (bins[parseInt(xScale.invert(s[1]))].x0 * bucketSize).toFixed(2);
        });

        handle
          .attr("display", null)
          .attr(
            "transform",
            (d, i) => "translate(" + [s[i], -height / 4] + ")"
          );
      })
      .on("end", function ({ sourceEvent, selection, target }) {
        if (!sourceEvent) return;

        let selectionRange = selection.map(
          (d) => bucketSize * Math.round(xScale.invert(d))
        );
        svg.node().value = selectionRange;

        selectedSims = [];
        for (let i = selectionRange[0]; i < selectionRange[1]; i++) {
          selectedSims.push(...binValues[i].map((v) => v.simId));
        }

        var d0 = selection.map(xScale.invert);
        var d1 = d0.map(Math.round);
        d3.select(this).transition().call(target.move, d1.map(xScale));
      });

    var gBrush = g.append("g").attr("class", "brush").call(brush);

    var brushResizePath = function (d) {
      var e = +(d.type == "e"),
        x = e ? 1 : -1,
        y = height / 2;
      return (
        "M" +
        0.5 * x +
        "," +
        y +
        "A6,6 0 0 " +
        e +
        " " +
        6.5 * x +
        "," +
        (y + 6) +
        "V" +
        (2 * y - 6) +
        "A6,6 0 0 " +
        e +
        " " +
        0.5 * x +
        "," +
        2 * y +
        "Z" +
        "M" +
        2.5 * x +
        "," +
        (y + 8) +
        "V" +
        (2 * y - 8) +
        "M" +
        4.5 * x +
        "," +
        (y + 8) +
        "V" +
        (2 * y - 8)
      );
    };

    var handle = gBrush
      .selectAll(".handle--custom")
      .data([{ type: "w" }, { type: "e" }])
      .enter()
      .append("path")
      .attr("class", "handle--custom")
      .attr("stroke", "#888")

      .attr("cursor", "ew-resize")
      .attr("d", brushResizePath);

    gBrush
      .selectAll(".overlay")
      .each(function (d) {
        d.type = "selection";
      })
      .on("mousedown touchstart", brushcentered);

    function brushcentered(event) {
      var dx = xScale(1) - xScale(0),
        cx = d3.pointer(event)[0],
        x0 = cx - dx / 2,
        x1 = cx + dx / 2;
      d3.select(this.parentNode).call(
        brush.move,
        x1 > width ? [width - dx, width] : x0 < 0 ? [0, dx] : [x0, x1]
      );
    }

    gBrush.call(
      brush.move,
      defaultRange
        .map((d) => width * (d / 100))
        .map(xScale.invert)
        .map(Math.round)
        .map(xScale)
    );

    svg.append("style").text(style);
  }

  onMount(() => {
    histogramSlider({ defaultRange: [0, 100], bucketSize: 1, w, h });
    el.append(svg.node());
  });

  let style = `
<style>
svg {
	font-family: -apple-system, system-ui, "avenir next", avenir, helvetica, "helvetica neue", ubuntu, roboto, noto, "segoe ui", arial, sans-serif;
}

rect.overlay {
	stroke: #888;
}

rect.selection {
	stroke: none;
  fill: gray;
  opacity: 0.5;
}

#labelleft, #labelright, #label-max, #label-min  {
  font-size: 18px;
}

#labelleft, #labelright {
	dominant-baseline: hanging;
}

#label-min, #label-max {
	dominant-baseline: central;
	text-anchor: end;
}

#labelleft {
	text-anchor: end;
}

#labelright {
	text-anchor: start;
}
</style>
`;
</script>

<div class="stat">
  <div bind:this={el} class="histogram-slider" />
</div>

<style>
  .histogram-slider {
    width: 100%;
  }
  .stat {
    height: 120px;
    padding: 12px 0px 12px 0px;
  }
</style>
