(function () {
    'use strict';


    var module = angular.module('ScriptBrowser.charts', []);

    module.directive('similarityGraph', function () {

        var SimilarityGraph = function ($element, attrs, onClicked) {

            var self = this;
            var $d3_element = d3.select($element[0]);

            var width = 450,
                height = 400,
                radius = 4,
                padding = 10;

            var iteration = 50;

            var color = d3.scale.category20();

            var force = d3.layout.force()
                .charge(-120)
                .linkDistance(function(d){ return 10 / d.similarity; })
                .size([width, height]);

            var svg = $d3_element.append("svg")
                .attr("width", width)
                .attr("height", height)
                .append("g")
                    .call(d3.behavior.zoom().scaleExtent([1, 8]).on("zoom", zoom))
                .append("g");

            function zoom() {
              var trans=d3.event.translate;
              var scale=d3.event.scale;

              svg.attr("transform",
                  "translate(" + trans + ")"
                  + " scale(" + scale + ")");
            }

            svg.on("dblclick.zoom", null);


            self.render = function (data) {

                force
                  .nodes(data.nodes)
                  .links(data.links);

                var link = svg.selectAll(".link")
                  .data(data.links)
                .enter().append("line")
                  .attr("class", "link")
                  .style("stroke-width", function(d) { return Math.sqrt(d.value); });

                link.append("title")
                  .text(function(d) { return d.similarity; });

                var node = svg.selectAll(".node")
                  .data(data.nodes)
                .enter().append("circle")
                    .attr("class", "node")
                    .attr("r", radius)
                    .on('click', function(d){
                        onClicked(d); // call external click function
                    });

                node.append("title")
                  .text(function(d) { return d.name; });

                force.on("tick", function() {
                //    node.attr("cx", function(d) { return d.x = Math.max(radius + padding, Math.min(width - radius - padding, d.x)); })
                //        .attr("cy", function(d) { return d.y = Math.max(radius + padding, Math.min(height - radius - padding, d.y)); });
                    node.attr("cx", function(d) { return d.x; })
                        .attr("cy", function(d) { return d.y; });

                    link.attr("x1", function(d) { return d.source.x; })
                        .attr("y1", function(d) { return d.source.y; })
                        .attr("x2", function(d) { return d.target.x; })
                        .attr("y2", function(d) { return d.target.y; });

                });

                var loading = svg.append("text")
                    .attr("x", width / 2)
                    .attr("y", height / 2)
                    .attr("dy", ".35em")
                    .style("text-anchor", "middle")
                    .text("Simulating. One moment please");

                // Use a timeout to allow the rest of the page to load first.
                setTimeout(function() {

                    // Run the layout a fixed number of times.
                    // The ideal number of times scales with graph complexity.
                    // Of course, don't run too long or you'll hang the page!
                    force.start();
                    for (var i = iteration * iteration; i > 0; --i) force.tick();
                    force.stop();

                    loading.remove();
                }, 10);
            };

        };

        function link(scope, $element, attrs) {
            if (!scope._vis) {
                var vis = scope._vis = new SimilarityGraph($element, attrs, scope.onClicked);
                scope.$watch('data', function (newVals, oldVals) {
                    if (newVals)
                        return vis.render(scope.data);
                }, false);


            } else {
                throw("What is this madness");
            }
        }

        return {
            //Use as a tag only
            restrict: 'E',
            replace: false,

            //Directive's inner scope
            scope: {
                data: '=data',
                onClicked: '=onClicked'
            },
            link: link,
            transclude: true,
            template: '<div class="render-target"></div>' +
            '<div ng-transclude></div>'
        }
    });

    module.directive('relationGraph', function () {

        var RelationGraph = function ($element, attrs, onClicked) {

             var self = this;
            var $d3_element = d3.select($element[0]);

            var width = 800,
                height = 800,
                padding = 10;


            var svg = $d3_element.append("svg")
                .attr("width", width)
                .attr("height", height);
            var g = svg.append("g");
            var zoom = d3.behavior.zoom().on("zoom", function() {
                g.attr("transform", "translate(" + d3.event.translate + ")" +
                                            "scale(" + d3.event.scale + ")");
              });
            svg.call(zoom);

            svg.on("dblclick.zoom", null);

            var scroll_to_line = function(line_no){
               // var first_line = $("#line_" + line_no);
                //first_line[0].scrollIntoView();
            };
            var current_selected = undefined;

            var render = new dagreD3.render();
            self.render = function (data) {
                // Run the renderer. This is what draws the final graph.
                var graph = new dagreD3.graphlib.Graph().setGraph({});
                    graph.setDefaultEdgeLabel(function() { return {}; });
                data.nodes.forEach(function(node){
                    node.label = node.name;
                    node.rx = node.ry = 5;
                    graph.setNode(node.id, node);
                });
                data.links.forEach(function(link){
                    graph.setEdge(link.source, link.target, link);
                });

                render(g, graph);
                // Center the graph
                var initialScale = 0.75;
                zoom
                  .translate([(svg.attr("width") - graph.graph().width * initialScale) / 2, 20])
                  .scale(initialScale)
                  .event(svg);
                svg.attr('height', height - padding * 2);

                g.selectAll("g.node")
                    .on("click", function(d){
                        var node = graph.node(d);
                        /*d3.selectAll("#code .line").classed("active", false);
                        d3.selectAll("#vis rect").classed("active", false);
                        d3.selectAll("#vis .edgePath").classed("active", false);*/

                        if (current_selected != node){
                            /*if (node.lines.length > 0){
                                node.lines.forEach(function(line){
                                    d3.selectAll("#line_" + line).classed("active", true);
                                });
                                scroll_to_line(node.lines[0]);
                            }


                            d3.select(this).select("rect").classed("active", true);*/
                            current_selected = node;
                            onClicked(node);
                        }
                        else{
                            current_selected = undefined;
                            onClicked(undefined);
                        }
                    }
                    );

                g.selectAll("g.edgePath").each(function(edge_id){
                    var edge = graph.edge(edge_id);
                    var self = d3.select(this);
                    self.classed(edge.relation, true);
                    /*if (edge.hasOwnProperty("line_no")){
                        self.classed("clickable", true);
                        self.on("click", function(d){
                            var edge = graph.edge(d);
                            d3.selectAll("#code .line").classed("active", false);
                            d3.selectAll("#vis rect").classed("active", false);
                            d3.selectAll("#vis .edgePath").classed("active", false);
                            if (current_selected != edge){
                                self.classed("active", true);
                                d3.selectAll("#line_" + edge.line_no).classed("active", true);
                                scroll_to_line(edge.line_no);
                                current_selected = edge;
                                onClicked(edge.type);
                            }
                            else{
                                current_selected = undefined;
                                onClicked(undefined);
                            }
                        });
                    }*/
                });

            };


        };

        function link(scope, $element, attrs) {
            if (!scope._vis) {
                var vis = scope._vis = new RelationGraph($element, attrs, scope.onClicked);
                scope.$watch('data', function (newVals, oldVals) {
                    if (newVals)
                        return vis.render(scope.data);
                }, false);


            } else {
                throw("What is this madness");
            }
        }

        return {
            //Use as a tag only
            restrict: 'E',
            replace: false,

            //Directive's inner scope
            scope: {
                data: '=data',
                onClicked: '=onClicked'
            },
            link: link,
            transclude: true,
            template: '<div class="render-target"></div>' +
            '<div ng-transclude></div>'
        }
    });

    module.directive('commonCallGraph', function () {

        var RadialTree = function ($element, attrs, onClicked) {

            var self = this;
            var $d3_element = d3.select($element[0]);
            var margin = {top: 20, right: 120, bottom: 20, left: 120},
                width = 600 - margin.right - margin.left,
                height = 400 - margin.top - margin.bottom;


            var tree = d3.layout.tree()
                .size([height, width])
                .children(function(d){ return d.neighbors });


            var diagonal = d3.svg.diagonal()
                .projection(function(d) { return [d.y, d.x]; });

            var svg = $d3_element.append("div")
                .attr("width", width + margin.right + margin.left)
                .attr("height", height + margin.top + margin.bottom)
              .append("g")
                .attr("transform", "translate(" + margin.left + "," + margin.top + ")");


            self.render = function (data) {
                var nodes = tree.nodes(data);
                var links = tree.links(nodes);

                var link = svg.selectAll(".link")
                  .data(links)
                    .attr("d", diagonal);

                link.enter().append("path")
                  .attr("class", "link");


                link.exit().remove();

                var node = svg.selectAll(".node")
                  .data(nodes)
                    .attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; })
                    .each(function(d){
                        var self = d3.select(this);
                        self.attr("transform", function(d) { return "translate(" + d.y + "," + d.x + ")"; });
                        self.select('text')
                          .attr("dx", function(d) { return d.name == data.name ? -8 : 8; })
                          .attr("dy", 3)
                          .attr("text-anchor", function(d) { return d.name == data.name ? "end" : "start"; })
                          .text(function(d) { return d.name; });
                    });

                node.exit().remove();


                var nodeNg = node.enter().append("g")
                    .attr("class", "node");
                  //.attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; });

                nodeNg.append("circle")
                  .attr("r", 4.5);

                nodeNg.append("text");




            };



        };

        function link(scope, $element, attrs) {
            if (!scope._vis) {
                var vis = scope._vis = new RadialTree($element, attrs, scope.onClicked);
                scope.$watch('data', function (newVals, oldVals) {
                    if (newVals){
                        return vis.render(scope.data);
                    }

                }, false);


            } else {
                throw("What is this madness");
            }
        }

        return {
            //Use as a tag only
            restrict: 'E',
            replace: false,

            //Directive's inner scope
            scope: {
                data: '=data',
                onClicked: '=onClicked'
            },
            link: link,
            transclude: true,
            template: '<div class="render-target"></div>' +
            '<div ng-transclude></div>'
        }
    });


})();
