(function () {
    'use strict';


    var module = angular.module('ScriptBrowser.charts', []);

    module.directive('similarityGraph', function () {

        var SimilarityGraph = function ($element, attrs, onClicked) {

            var self = this;
            var $d3_element = d3.select($element[0]);

            var width = 700,
                height = 650,
                radius = 4,
                padding = 10;

            var iteration = 5;

            var color = d3.scale.category20();

            var force = d3.layout.force()
                .charge(-120)
                .linkDistance(function(d){ return 10 / d.similarity; })
                .size([width, height]);

            var svg = $d3_element.append("svg")
                .attr("width", width)
                .attr("height", height);


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
                        d.neighbors = d.links; // TODO: remove the ref when defocus
                        onClicked(d); // call external click function
                    });

                node.append("title")
                  .text(function(d) { return d.name; });

                force.on("tick", function() {
                    node.attr("cx", function(d) { return d.x = Math.max(radius + padding, Math.min(width - radius - padding, d.x)); })
                        .attr("cy", function(d) { return d.y = Math.max(radius + padding, Math.min(height - radius - padding, d.y)); });
                //node.attr("cx", function(d) { return d.x; })
                //    .attr("cy", function(d) { return d.y; });

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

    module.directive('commonCallGraph', function () {

        var RadialTree = function ($element, attrs, onClicked) {

            var self = this;
            var $d3_element = d3.select($element[0]);
            var diameter = 500;

            var tree = d3.layout.tree()
                .size([360, diameter / 2 - 120])
                .children(function(d){ return d.neighbors })
                .separation(function(a, b) { return (a.parent == b.parent ? 1 : 2) / a.depth; });

            var diagonal = d3.svg.diagonal.radial()
                .projection(function(d) { return [d.y, d.x / 180 * Math.PI]; });

            var svg = $d3_element.append("svg")
                .attr("width", diameter)
                .attr("height", diameter - 150)
              .append("g")
                .attr("transform", "translate(" + diameter / 2 + "," + diameter / 2 + ")");


            self.render = function (data) {
                var nodes = tree.nodes(data);
                var links = tree.links(nodes);

                var link = svg.selectAll(".link")
                  .data(links)
                .enter().append("path")
                  .attr("class", "link")
                  .attr("d", diagonal);

                var node = svg.selectAll(".node")
                  .data(nodes)
                .enter().append("g")
                  .attr("class", "node")
                  .attr("transform", function(d) { return "rotate(" + (d.x - 90) + ")translate(" + d.y + ")"; });

                node.append("circle")
                  .attr("r", 4.5);

                node.append("text")
                  .attr("dy", ".31em")
                  .attr("text-anchor", function(d) { return d.x < 180 ? "start" : "end"; })
                  .attr("transform", function(d) { return d.x < 180 ? "translate(8)" : "rotate(180)translate(-8)"; })
                  .text(function(d) { return d.name; });
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
