

var w=700,h=500;

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

var outerRadius=Math.min(w, h) / 2;
var innerRadius=outerRadius - 80;

var arc=d3.svg.arc()
        .outerRadius(outerRadius)
        .innerRadius(innerRadius);


var pie=d3.layout.pie()
        .value(function(d){return d.percent})
        .sort(null)
        .padAngle(0.02);


//tooltip creation
var div = d3.select("body").append("div")
    .attr("class", "tooltip")
    .style("opacity", 0);


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
  .text(function(d){ if (d.data.percent>2){
  	return d.data.percent.toFixed(2)+"%";
  }})
  ;


//Creation of the legend
var legendRectSize=20;
var legendSpacing=7;
var legendHeight=legendRectSize+legendSpacing;


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
		  transform:function(d,i){
			  //Just a calculation for x and y position
			  return 'translate(-35,' + 15 + ')';
		  }
	  });


//button
function change(asd) {
	var rawData = asd;


	var w=700,h=500;

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

	var outerRadius=Math.min(w, h) / 2;
	var innerRadius=outerRadius - 80;

	var arc=d3.svg.arc()
			.outerRadius(outerRadius)
			.innerRadius(innerRadius);


	var pie=d3.layout.pie()
			.value(function(d){return d.percent})
			.sort(null)
			.padAngle(0.02);


	//tooltip creation
	var div = d3.select("body").append("div")
		.attr("class", "tooltip")
		.style("opacity", 0);


	var path=svg.selectAll('path')
			.data(pie(rawData))
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
	  .data(pie(rawData))
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
	  .text(function(d){ if (d.data.percent>2){
		return d.data.percent.toFixed(2)+"%";
	  }})
	  ;


	//Creation of the legend
	var legendRectSize=20;
	var legendSpacing=7;
	var legendHeight=legendRectSize+legendSpacing;


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
		.html("£" + total_bet.toFixed(2))
		.attr({
			  class:'total',
			  transform:function(d,i){
				  //Just a calculation for x and y position
				  return 'translate(-35,' + 15 + ')';
			  }
		  });


  }



// d3.select("#update")
// 	.on("click", function() {
// 		change();
// 	})








// var svg = d3.select("body")
// 	.append("svg")
// 	.append("g")
//
// svg.append("g")
// 	.attr("class", "slices");
// svg.append("g")
// 	.attr("class", "labels");
// svg.append("g")
// 	.attr("class", "lines");
//
// var width = 960,
//     height = 450,
// 	radius = Math.min(width, height) / 2;
//
// var pie = d3.layout.pie()
// 	.sort(null)
// 	.value(function(d) {
// 		return d.value;
// 	});
//
// var arc = d3.svg.arc()
// 	.outerRadius(radius * 0.8)
// 	.innerRadius(radius * 0.4);
//
// var outerArc = d3.svg.arc()
// 	.innerRadius(radius * 0.9)
// 	.outerRadius(radius * 0.9);
//
// svg.attr("transform", "translate(" + width / 2 + "," + height / 2 + ")");
//
// var key = function(d){ return d.data.label; };
//
// var color = d3.scale.ordinal()
// 	.domain(["Lorem ipsum", "dolor sit", "amet", "consectetur", "adipisicing", "elit", "sed", "do", "eiusmod", "tempor", "incididunt"])
// 	.range(["#98abc5", "#8a89a6", "#7b6888", "#6b486b", "#a05d56", "#d0743c", "#ff8c00"]);
//
// // var asdfh = [4,5,6,7,1,7,8,3]
//
// function randomData (){
// 	var labels = color.domain();
// 	return labels.map(function(label){
// 		return { label: label, value: asdfh[labels.indexOf(label)]}
// 	});
// }
//
// change(randomData());
//
// d3.select(".updatebutton")
// 	.on("click", function(){
// 		change(randomData());
// 	});
//
//
// function change(data) {
//
// 	/* ------- PIE SLICES -------*/
// 	var slice = svg.select(".slices").selectAll("path.slice")
// 		.data(pie(data), key);
//
// 	slice.enter()
// 		.insert("path")
// 		.style("fill", function(d) { return color(d.data.label); })
// 		.attr("class", "slice");
//
// 	slice
// 		.transition().duration(1000)
// 		.attrTween("d", function(d) {
// 			this._current = this._current || d;
// 			var interpolate = d3.interpolate(this._current, d);
// 			this._current = interpolate(0);
// 			return function(t) {
// 				return arc(interpolate(t));
// 			};
// 		})
//
// 	slice.exit()
// 		.remove();
//
// 	/* ------- TEXT LABELS -------*/
//
// 	var text = svg.select(".labels").selectAll("text")
// 		.data(pie(data), key);
//
// 	text.enter()
// 		.append("text")
// 		.attr("dy", ".35em")
// 		.text(function(d) {
// 			return d.data.label;
// 		});
//
// 	function midAngle(d){
// 		return d.startAngle + (d.endAngle - d.startAngle)/2;
// 	}
//
// 	text.transition().duration(1000)
// 		.attrTween("transform", function(d) {
// 			this._current = this._current || d;
// 			var interpolate = d3.interpolate(this._current, d);
// 			this._current = interpolate(0);
// 			return function(t) {
// 				var d2 = interpolate(t);
// 				var pos = outerArc.centroid(d2);
// 				pos[0] = radius * (midAngle(d2) < Math.PI ? 1 : -1);
// 				return "translate("+ pos +")";
// 			};
// 		})
// 		.styleTween("text-anchor", function(d){
// 			this._current = this._current || d;
// 			var interpolate = d3.interpolate(this._current, d);
// 			this._current = interpolate(0);
// 			return function(t) {
// 				var d2 = interpolate(t);
// 				return midAngle(d2) < Math.PI ? "start":"end";
// 			};
// 		});
//
// 	text.exit()
// 		.remove();
//
// 	/* ------- SLICE TO TEXT POLYLINES -------*/
//
// 	var polyline = svg.select(".lines").selectAll("polyline")
// 		.data(pie(data), key);
//
// 	polyline.enter()
// 		.append("polyline");
//
// 	polyline.transition().duration(1000)
// 		.attrTween("points", function(d){
// 			this._current = this._current || d;
// 			var interpolate = d3.interpolate(this._current, d);
// 			this._current = interpolate(0);
// 			return function(t) {
// 				var d2 = interpolate(t);
// 				var pos = outerArc.centroid(d2);
// 				pos[0] = radius * 0.95 * (midAngle(d2) < Math.PI ? 1 : -1);
// 				return [arc.centroid(d2), outerArc.centroid(d2), pos];
// 			};
// 		});
//
// 	polyline.exit()
// 		.remove();
// };