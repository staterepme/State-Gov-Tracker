<script type="text/javascript" src="http://d3js.org/d3.v2.js"></script>
function draw_graph() {
    var margin = 50,
        side_margin = 20,
        width = $("#bio_right").width(),
        height = 100;

    // add x, y scales
    var x = d3.scale.linear().range([0+side_margin, width-side_margin]).domain([{{ graph_data.x_min }}, {{  graph_data.x_max  }}]);
    var y = d3.scale.linear().range([height, 0]).domain([0, {{ graph_data.y_max }}]);

    // map data to an area, use "monotone" interpolation
    var area = d3.svg.area()
        .interpolate("monotone")
        .x(function(d) { return x(d.x_axis); })
        .y0(height)
        .y1(function(d) { return y(d.y_axis); });

    // add svg element to DOM, with desired size
    var svg = d3.select("svg#pref_distribution")
        .append("svg")
        .attr("width", width)
        .attr("height", height + margin);

    var rep_distribution = d3.select("svg#pref_distribution")
        .append("g")
        .attr("width", width)
        .attr("height", height);

    var dem_distribution = d3.select("svg#pref_distribution")
        .append("g")
        .attr("class", "dem_distribution")
        .attr("width", width)
        .attr("height", height);

    var bar = d3.select("svg#pref_distribution")
        .attr("width", width)
        .attr("height", height + margin);

    // Add Republicans from State Senate //

    {% autoescape off %}
    var dem_data = {{ graph_data.dem }};
    var rep_data = {{ graph_data.rep }};
    {% endautoescape %}

    function myReps(data) {
      data.forEach(function(d) {
        d.x_axis = +d.x_axis
        d.y_axis = +d.y_axis;
      });

      rep_distribution.append("path")
        .attr("class", "rep_distribution")
        .data([data])
        .attr("d", area)
    };

    // Add Democrats from State Senate //
    function myDems(data) {
      data.forEach(function(d) {
        d.x_axis = +d.x_axis;
        d.y_axis = +d.y_axis;
      });

      // render data as a path element, using area function
      dem_distribution.append("path")
          .data([data])
          .attr("d", area)
    };
    myDems(dem_data);
    myReps(rep_data);
    
    // X Axis
    var x_axis = d3.svg.axis().scale(x);
    d3.select("svg#pref_distribution")
        .append("g")
        .attr("class", "x axis")
        .attr("transform", "translate(0," + (height) + ")")
        .call(x_axis);

    // Y Axis
    var y_axis = d3.svg.axis().scale(y).orient("left");

    // X-Axis Titles //
    d3.select(".x.axis")
        .append("text")
        .text("Liberal")
        .attr("transform", "translate("+0+side_margin+",30)");
    axis_label = width-side_margin;
    d3.select(".x.axis")
        .append("text")
        .text("Conservative")
        .attr("transform", "translate("+axis_label+",30)")
        .attr("text-anchor", "end");
    center_axis_label = width/2
    d3.select(".x.axis")
        .append("text")
        .text("Distribution of Political Ideology")
        .attr("transform", "translate("+center_axis_label+",40)")
        .attr("text-anchor", "middle");

    var position = {{ ideology }};

    var dataposition = [{"value":position}];

    var datalabel = [{"value":position, "name":"Ideal point of"}, {"value":position, "name":"{{ official.fullname }}"}]

    var bw = 3;

    bar.selectAll("rect.bar")
        .data(dataposition)
        .enter()
        .append("rect")
        .attr("class", "bar")
        .attr("x", function(d) {
            return x(d['value'])-1;
        })
        .attr("width", bw-1)
        .attr("y", function(d) {
            return height - y(0);
        })
        .attr("height", function(d) {
            return y(0);
        });

    // Label of bar //
    bar.selectAll("label")
        .data(datalabel)
        .enter()
        .append("text")
        .attr("x", function(d) {
            return x(d['value'])+3;
        })
        .attr("y", function(d, i) {
            return (i+1)*12;
        })
        .style("fill", "white")
        .style("z-index", "99999999")
        .text(function(d) {
            return (d['name']);
        });
};
