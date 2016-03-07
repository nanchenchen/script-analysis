(function () {
    'use strict';


    var module = angular.module('ScriptVarGraph.charts', []);

    module.directive('varGraph', function () {

        var VarGraph = function ($element, attrs, onClicked) {

            var self = this;
            var $d3_element = d3.select($element[0]);

            var width = 800,
                height = 800,
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
                .attr("height", height);
            var g = svg.append("g");
            var zoom = d3.behavior.zoom().on("zoom", function() {
                g.attr("transform", "translate(" + d3.event.translate + ")" +
                                            "scale(" + d3.event.scale + ")");
              });
            svg.call(zoom);

            svg.on("dblclick.zoom", null);

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
                    graph.setEdge(link.source, link.target);
                });

                render(g, graph);
                // Center the graph
                var initialScale = 0.75;
                zoom
                  .translate([(svg.attr("width") - graph.graph().width * initialScale) / 2, 20])
                  .scale(initialScale)
                  .event(svg);
                svg.attr('height', height * initialScale + 40);

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
