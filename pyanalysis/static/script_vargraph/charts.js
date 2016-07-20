(function () {
    'use strict';


    var module = angular.module('ScriptVarGraph.charts', []);

    module.directive('varGraph', function () {

        var VarGraph = function ($element, attrs, onClicked) {

            var self = this;
            var $d3_element = d3.select($element[0]);

            var width = 780,
                height = 590,
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
                var first_line = $("#line_" + line_no);
                first_line[0].scrollIntoView();
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
                        d3.selectAll("#code .line").classed("active", false);
                        d3.selectAll("#vis rect").classed("active", false);
                        d3.selectAll("#vis .edgePath").classed("active", false);

                        if (current_selected != node){
                            if (node.lines.length > 0){
                                node.lines.forEach(function(line){
                                    d3.selectAll("#line_" + line).classed("active", true);
                                });
                                scroll_to_line(node.lines[0]);
                            }


                            d3.select(this).select("rect").classed("active", true);
                            current_selected = node;
                            onClicked("node");
                        }
                        else{
                            current_selected = undefined;
                            onClicked(undefined);
                        }

                    });

                g.selectAll("g.edgePath").each(function(edge_id){
                    var edge = graph.edge(edge_id);
                    var self = d3.select(this);
                    self.classed(edge.type, true);
                    if (edge.hasOwnProperty("line_no")){
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
                    }
                });

            }


        };

        function link(scope, $element, attrs) {
            if (!scope._vis) {
                var vis = scope._vis = new VarGraph($element, attrs, scope.onClicked);
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


})();
