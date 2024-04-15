
<script>
    import { setContext } from 'svelte';
    import * as d3 from 'd3';

    const svg = d3
      .create("svg")
      .attr("preserveAspectRatio", "xMidYMid meet")
      .attr("viewBox", [0, 0, 600, 600])
      .style("background-color", "hsl(var(--nc))");

    setContext("svg", svg);
</script>