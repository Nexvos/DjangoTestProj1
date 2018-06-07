// //svg size variables - also controls size of pie --- Trying to make the pie page size reactive
var w= (document.getElementsByClassName('jumbotron')[0].clientWidth) * 0.42;
var h= w *0.75;



console.log(w);
console.log(h);

// //legend variables
var legendRectSize=20;
var legendSpacing=7;
var legendHeight=legendRectSize+legendSpacing;


//sorting function
var sort_by;

(function() {
    // utility functions
    var default_cmp = function(a, b) {
            if (a == b) return 0;
            return a < b ? -1 : 1;
        },
        getCmpFunc = function(primer, reverse) {
            var dfc = default_cmp, // closer in scope
                cmp = default_cmp;
            if (primer) {
                cmp = function(a, b) {
                    return dfc(primer(a), primer(b));
                };
            }
            if (reverse) {
                return function(a, b) {
                    return -1 * cmp(a, b);
                };
            }
            return cmp;
        };

    // actual implementation
    sort_by = function() {
        var fields = [],
            n_fields = arguments.length,
            field, name, reverse, cmp;

        // preprocess sorting options
        for (var i = 0; i < n_fields; i++) {
            field = arguments[i];
            if (typeof field === 'string') {
                name = field;
                cmp = default_cmp;
            }
            else {
                name = field.name;
                cmp = getCmpFunc(field.primer, field.reverse);
            }
            fields.push({
                name: name,
                cmp: cmp
            });
        }

        // final comparison function
        return function(A, B) {
            var a, b, name, result;
            for (var i = 0; i < n_fields; i++) {
                result = 0;
                field = fields[i];
                name = field.name;

                result = field.cmp(A[name], B[name]);
                if (result !== 0) break;
            }
            return result;
        }
    }
}());

function InitialPie(dataset, totalamount) {

	//sort the data
	dataset.sort(sort_by('team','name',{name:'amount',primer:parseInt,reverse:false}));

	//Create the SVG with correct attributes and transformed g element
	var svg=d3.select("#chart")
			.append("svg")
			.attr({
				width:w,
				height:h,
				class:'shadow'
			}).append('g')
			.attr({
				transform:'translate('+w/2+','+h/2+')'
			});

	//Set outer and inner radius of the donut
	var outerRadius=Math.min(w, h) / 2;
	var innerRadius=outerRadius *0.78;

	//Create d3 arc - This sets up the creation of the
	var arc=d3.svg.arc()
			.outerRadius(outerRadius)
			.innerRadius(innerRadius);

	//Create pie
	var pie=d3.layout.pie()
			.value(function(d){return d.percent})
			.sort(null)
			.padAngle(0.02);

	// Creates the pie elements
	var path=svg.selectAll('path')
			.data(pie(dataset))
			.enter()
			.append('path')
			.attr({
				d:arc,
				fill: function(d,i){
					return color(d.data.name);
				}
			})
			//tooltip mouseover animation
			.on("mouseover", mouseover)
			.on("mouseout", mouseout);


	//tooltip creation
	var div = d3.select("body").append("div")
		.attr("class", "tooltip")
		.style("opacity", 0);

	function mouseover(d) {
		d3.select(this).transition()
			.duration(200)
			.style("stroke", "black")
			.style("stroke-width", "1");
		div.transition()
			.duration(200)
			.style("opacity", .85)
			.style("background", color(d.data.name));
		div.html("Name: " + d.data.name + "<br>" + "£" + d.data.amount.toFixed(2)+ "<br>" + d.data.team)
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		};

	function mouseout(d) {
		d3.select(this).transition()
			.duration(200)
			.style("stroke", "none");
		div.transition()
			.duration(500)
			.style("opacity", 0);
	};

	// Animation of the pie elements
	path.transition()
		.duration(800)
		.attrTween('d', function(d) {
			var interpolate = d3.interpolate({startAngle: 0, endAngle: 0}, d);
			return function(t) {
				return arc(interpolate(t));
			};
		});

	//percentage text
	var text=svg.selectAll('text')
	  .data(pie(dataset))
	  .enter()
	  .append("text")
	  .transition()
	  .duration(1000)
	  .attr("transform", function (d) {
		  return "translate(" + arc.centroid(d) + ")";
	  })
	  .attr("dy", ".4em")
	  .attr("text-anchor", "middle")
	  .attr("class", "strokeme")
	  .attr("id", "percentagetext")
	  .text(function(d){ if (d.data.percent>2){
		return d.data.percent.toFixed(2)+"%";
	  }})
	  ;


	//Creation of the legend
	var legend=svg.selectAll('.legend')
	  .data(color.domain())
	  .enter()
	  .append('g')
	  .attr({
		  class:'legend',
		  transform:function(d,i){
			  //Just a calculation for x and y position
			  return 'translate('+ (outerRadius + 30) + ',' + ((i*legendHeight) - h/2 +100) + ')';
		  }
	  });


	legend.append('rect')
	  .attr({
		  width:legendRectSize,
		  height:legendRectSize,
		  rx:20,
		  ry:20
	  })
	  .style({
		  fill:color,
		  stroke:color
	  });

	legend.append('text')
	  .attr({
		  x:30,
		  y:15
	  })
	  .text(function(d){
		  return d;
	  });

	//total
	var totalLabel = svg.append("text")
		.html("Total money bet:")
		.attr({
			  class:'total',
			  transform:function(d,i){
				  //Just a calculation for x and y position
				  return 'translate(-70,' + -15 + ')';
			  }
		  });
	var total = svg.append("text")
		.html("£" + totalamount.toFixed(2))
		.attr({
			  class:'total',
			  "id":'totalMoney',
			  transform:function(d,i){
				  //Just a calculation for x and y position
				  return 'translate(-35,' + 15 + ')';
			  }
		  })
};


//button
function change(asd, ads) {

	//sort data by amount -> person -> team
	// asd.sort(sort_by('amount',false,parseInt));
	// asd.sort(sort_by('name',false,function(a){return a.toUpperCase()}));
	// asd.sort(sort_by('team',false,function(a){return a.toUpperCase()}));
	asd.sort(sort_by('team','name',{name:'amount',primer:parseInt,reverse:false}));

    var svg = d3.select("#chart")
		.select("svg")
		.select("g");

    // var oldData = svg.selectAll("path")
    //  .data().map(function(d) { return d.data });
    // console.log(oldData);

    var path = svg.selectAll('path')

	var pie=d3.layout.pie()
			.value(function(d){return d.percent})
			.sort(null)
			.padAngle(0.02);
    //tooltip creation

	var outerRadius=Math.min(w, h) / 2;
	var innerRadius=outerRadius - 80;

	var arc=d3.svg.arc()
			.outerRadius(outerRadius)
			.innerRadius(innerRadius);

    path.each(function (d) {
        this._current = d;
    }); // store the initial angles


    path.data(pie(asd));
    path.transition().duration(750).attrTween("d", arcTween); // redraw the arcs
    // console.log(asd);

    // path.data(pie(oldData))
    // 	.exit();

    $("#fadein").attr("id", "");



    path.data(pie(asd))
        .enter()
        .append('path')
        .attr({
            d: arc,
            fill: function (d, i) {
                return color(d.data.name);
            },
            "id": "fadein"
        })
        //tooltip mouseover animation
        .on("mouseover", mouseover)
        .on("mouseout", mouseout);

    var div = d3.select("body").append("div")
		.attr("class", "tooltip")
		.style("opacity", 0);

	function mouseover(d) {
		d3.select(this).transition()
			.duration(200)
			.style("stroke", "black")
			.style("stroke-width", "1");
		div.transition()
			.duration(200)
			.style("opacity", .85)
			.style("background", color(d.data.name));
		div.html("Name: " + d.data.name + "<br>" + "£" + d.data.amount.toFixed(2))
			.style("left", (d3.event.pageX) + "px")
			.style("top", (d3.event.pageY - 28) + "px");
		};

	function mouseout(d) {
		d3.select(this).transition()
			.duration(200)
			.style("stroke", "none");
		div.transition()
			.duration(500)
			.style("opacity", 0);
	};

    path.transition().duration(750).attrTween("d", arcTween);


    $("#fadein").hide().fadeIn(3000);


    function arcTween(a) {
        var i = d3.interpolate(this._current, a);
        this._current = i(0);
        return function (t) {
            return arc(i(t));
        };
    }

    //Percentage Text
	var text=svg.selectAll('#percentagetext')
	    .data(pie(asd))
	 	.enter()
		.append("text")
		.attr("id", "percentagetext");
	svg.selectAll('#percentagetext').transition()
	  .duration(1000)
	  .attr("transform", function (d) {
		  return "translate(" + arc.centroid(d) + ")";
	  })
	  .attr("dy", ".4em")
	  .attr("text-anchor", "middle")
	  .attr("class", "strokeme")
	  .text(function(d){ if (d.data.percent>2){
		return d.data.percent.toFixed(2)+"%";
	  }})
	  ;


		//Creation of the legend
	var legend=svg.selectAll('.legend')
	  .data(color.domain())
	  .enter()
	  .append('g')
	  .attr({
		  class:'legend',
		  transform:function(d,i){
			  //Just a calculation for x and y position
			  return 'translate('+ (outerRadius + 50) + ',' + ((i*legendHeight) - h/2 +100) + ')';
		  }
	  });

	legend.append('rect')
	  .attr({
		  width:legendRectSize,
		  height:legendRectSize,
		  rx:20,
		  ry:20
	  })
	  .style({
		  fill:color,
		  stroke:color
	  });

	legend.append('text')
	  .attr({
		  x:30,
		  y:15
	  })
	  .text(function(d){
		  return d;
	  });


	//adjust total
	svg.select("#totalMoney")
		.html("£" + ads.toFixed(2));
};

