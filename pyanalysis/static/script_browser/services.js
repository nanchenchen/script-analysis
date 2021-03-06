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

    //A service for loading relation graph.
    module.factory('ScriptBrowser.services.RelationGraph', [
        '$rootScope', '$http', 'djangoUrl',
        function relationGraphFactory($rootScope, $http, djangoUrl) {



            var RelationGraph = function () {
                var self = this;
                self.data = undefined;
            };

            angular.extend(RelationGraph.prototype, {
                construct_node_links: function(data){
                    var self = this;
                    /*data.nodes.forEach(function(d){
                       // d.links = [];
                        //d.id = "node_" + d.id;
                    });
                    data.links.forEach(function(d){
                        var src_node = data.nodes[d.source];
                        var tar_node = data.nodes[d.target];
                        src_node.links.push(tar_node);
                        tar_node.links.push(src_node);(

                       // d.source = "node_" + d.src_script;
                       // d.target = "node_" + d.tar_script;
                    });*/
                    return data;
                },

                load: function (dataset) {
                    var self = this;

                    var apiUrl = djangoUrl.reverse('relation-graph', {dataset_id: dataset});

                    return $http.get(apiUrl)
                        .success(function (data) {
                            self.data = self.construct_node_links(data);
                        });

                }
            });

            return new RelationGraph();
        }
    ]);


    //A service for loading similarity pairs.
    module.factory('ScriptBrowser.services.SimilarityPairs', [
        '$rootScope', '$http', 'djangoUrl',
        function similarityGraphFactory($rootScope, $http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('similarity-graph');

            var SimilarityPairs = function () {
                var self = this;
                self.data = undefined;
            };

            angular.extend(SimilarityPairs.prototype, {

                convert_links: function(data){
                    var self = this;

                    data.links.forEach(function(d){
                        d.source = data.nodes[d.source];
                        d.target = data.nodes[d.target];
                    });
                    return data.links;
                },

                load: function (dataset, metric, threshold) {
                    var self = this;

                    var request = {
                        params: {
                            id: dataset
                        }
                    };
                    if (metric) request.params.metric = metric;
                    if (threshold) request.params.threshold = threshold;

                    return $http.get(apiUrl, request)
                        .success(function (data) {
                            self.data = self.convert_links(data);
                        });

                }
            });

            return new SimilarityPairs();
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

    //A service for loading script comparator.
    module.factory('ScriptBrowser.services.Comparator', [
        '$http', 'djangoUrl',
        function scriptFactory($http, djangoUrl) {

            var apiUrl = djangoUrl.reverse('comparator');

            var Comparator = function () {
                var self = this;
                self.data = undefined;
            };

            angular.extend(Comparator.prototype, {
                load: function (dataset_id, src_id, tar_id) {
                    var self = this;

                    var request = {
                        params: {
                            id: dataset_id,
                            src_id: src_id,
                            tar_id: tar_id
                        }
                    };
                    return $http.get(apiUrl, request)
                        .success(function (data) {
                            self.data = data;
                        });

                },

                update_note: function(src_id, tar_id, relative_relation, note){
                    var self = this;
                    var request = {
                        src_script: src_id,
                        tar_script: tar_id,
                        relative_relation: relative_relation,
                        note: note
                    };
                    if (self.relative_relation == relative_relation && note == self.note) {
                        return false;
                    }
                    else {
                        return $http.post(apiUrl, request)
                            .success(function (data) {
                                self.note = data.note;
                            });
                    }

                }
            });

            return new Comparator();
        }
    ]);

})();
