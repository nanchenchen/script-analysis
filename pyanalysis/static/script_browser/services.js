(function () {
    'use strict';

    var module = angular.module('ScriptBrowser.services', [
        'ng.django.urls',
        'ScriptBrowser.bootstrap',
        'ngSanitize'
    ]);

    module.factory('ScriptBrowser.services.Dataset', [
        '$http', 'djangoUrl',
        'ScriptBrowser.bootstrap.dataset',
        function datasetFactory($http, djangoUrl, datasetId) {
            var apiUrl = djangoUrl.reverse('dataset');

            var Dataset = function () {
                this.id = datasetId
            };

            var request = {
                params: {
                    id: datasetId
                }
            };
            $http.get(apiUrl, request)
                .success(function (data) {
                    angular.extend(Dataset.prototype, data);
                });

            return new Dataset();

        }
    ]);


    //A service for loading similarity graph.
    module.factory('ScriptBrowser.services.SimilarityGraph', [
        '$rootScope', '$http', 'djangoUrl',
        function similarityGraphFactory($rootScope, $http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('similarity-graph');

            var SimilarityGraph = function () {
                var self = this;
                self.data = undefined;
            };

            angular.extend(SimilarityGraph.prototype, {
                focus_node: function(node){
                    node.neighbors = node.links;
                },
                defocus_node: function(node){
                    if (node.neighbors) node.neighbors = undefined;
                    if (node.children) node.children = undefined;

                },
                construct_node_links: function(data){
                    var self = this;
                    data.nodes.forEach(function(d){
                        d.links = [];
                    });
                    data.links.forEach(function(d){
                        var src_node = data.nodes[d.source];
                        var tar_node = data.nodes[d.target];
                        src_node.links.push(tar_node);
                        tar_node.links.push(src_node);
                    });
                    return data;
                },

                load: function (dataset) {
                    var self = this;

                    var request = {
                        params: {
                            id: dataset

                        }
                    };
                    return $http.get(apiUrl, request)
                        .success(function (data) {
                            self.data = self.construct_node_links(data);
                        });

                }
            });

            return new SimilarityGraph();
        }
    ]);


    //A service for loading script contents.
    module.factory('ScriptBrowser.services.Script', [
        '$http', 'djangoUrl',
        function scriptFactory($http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('script');

            var Script = function () {
                var self = this;
                self.data = undefined;
            };

            angular.extend(Script.prototype, {
                load: function (script_id) {
                    var self = this;

                    var request = {
                        params: {
                            id: script_id
                        }
                    };
                    return $http.get(apiUrl, request)
                        .success(function (data) {
                            self.data = data;
                        });

                }
            });

            return new Script();
        }
    ]);

})();
