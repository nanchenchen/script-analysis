(function () {
    'use strict';


    var module = angular.module('ScriptBrowser.controllers', [
        'ScriptBrowser.services',
        'angularSpinner',
        'ng-code-mirror',
        'angularResizable',
        'angucomplete-alt'
    ]);

    module.config(['$interpolateProvider', function ($interpolateProvider) {
        $interpolateProvider.startSymbol('{$');
        $interpolateProvider.endSymbol('$}');
    }]);


    module.config(['usSpinnerConfigProvider', function (usSpinnerConfigProvider) {
        usSpinnerConfigProvider.setDefaults({
            color: '#111'
        });
    }]);

    var DatasetController = function ($scope, Dataset) {
        $scope.Dataset = Dataset;

    };
    DatasetController.$inject = [
        '$scope',
        'ScriptBrowser.services.Dataset'
    ];
    module.controller('ScriptBrowser.controllers.DatasetController', DatasetController);

    var ViewController = function ($scope, Dataset, SimilarityGraph, Script, usSpinnerService) {

        $scope.spinnerOptions = {
            radius: 20,
            width: 6,
            length: 10,
            color: "#000000"
        };

        $scope.similarity_graph_data = undefined;
        $scope.script = undefined;
        $scope.focus_node = undefined;

        $scope.load = function(){
            var request = SimilarityGraph.load(Dataset.id);
            if (request) {
                usSpinnerService.spin('vis-spinner');
                request.then(function() {
                    usSpinnerService.stop('vis-spinner');
                    $scope.similarity_graph_data = SimilarityGraph.data;
                });
            }

        };
        $scope.highlight = function(call){
            var call_name = call.name.replace('.', '-');
            $('.' + call_name).addClass('highlight');
        };
        $scope.remove_highlight = function(){
            $('.highlight').removeClass('highlight');
        };

        $scope.click_node = function(script){
            console.log(script);
            if ($scope.focus_node){
                SimilarityGraph.defocus_node($scope.focus_node);
            }
            $scope.focus_node = script;
            SimilarityGraph.focus_node($scope.focus_node);
            var request = Script.load(script.id);
            if (request) {
                usSpinnerService.spin('code-spinner');
                request.then(function() {
                    usSpinnerService.stop('code-spinner');
                    $scope.script = Script.data;
                    PR.prettyPrint();
                });
            }
        };

        // load the similarity graph
        $scope.load();

    };
    ViewController.$inject = [
        '$scope',
        'ScriptBrowser.services.Dataset',
        'ScriptBrowser.services.SimilarityGraph',
        'ScriptBrowser.services.Script',
        'usSpinnerService'
    ];
    module.controller('ScriptBrowser.controllers.ViewController', ViewController);

    var RelationGraphController = function ($scope, Dataset, RelationGraph, Script, usSpinnerService) {

        $scope.spinnerOptions = {
            radius: 20,
            width: 6,
            length: 10,
            color: "#000000"
        };

        $scope.relation_graph_data = undefined;
        $scope.script = undefined;
        $scope.focus_node = undefined;

        $scope.load = function(){
            var request = RelationGraph.load(Dataset.id);
            if (request) {
                usSpinnerService.spin('vis-spinner');
                request.then(function() {
                    usSpinnerService.stop('vis-spinner');
                    $scope.relation_graph_data = RelationGraph.data;
                });
            }

        };


        $scope.click_node = function(script){
            console.log(script);
            $scope.focus_node = script;
            var request = Script.load(script.original_id);
            if (request) {
                usSpinnerService.spin('code-spinner');
                request.then(function() {
                    usSpinnerService.stop('code-spinner');
                    $scope.script = Script.data;
                    PR.prettyPrint();
                });
            }
        };

        // load the similarity graph
        $scope.load();

    };
    RelationGraphController.$inject = [
        '$scope',
        'ScriptBrowser.services.Dataset',
        'ScriptBrowser.services.RelationGraph',
        'ScriptBrowser.services.Script',
        'usSpinnerService'
    ];
    module.controller('ScriptBrowser.controllers.RelationGraphController', RelationGraphController);

    var ComparatorController = function ($scope, Dataset, SimilarityPairs, Comparator, usSpinnerService) {

        $scope.spinnerOptions = {
            radius: 20,
            width: 6,
            length: 10,
            color: "#000000"
        };

        $scope.similarity_pairs = undefined;
        $scope.source = undefined;
        $scope.target = undefined;
        $scope.diff = undefined;
        $scope.relative_relation = "U";
        $scope.options = [
            {value: "<", text: "<"},
            {value: "=", text: "="},
            {value: ">", text: ">"},
            {value: "?", text: "?"},
            {value: "U", text: "Undefined"},
        ];

        $scope.load = function(){
            var request = SimilarityPairs.load(Dataset.id, 'cosine', 0.8);
            if (request) {
                usSpinnerService.spin('vis-spinner');
                request.then(function() {
                    usSpinnerService.stop('vis-spinner');
                    $scope.similarity_pairs = SimilarityPairs.data;
                });
            }

        };


        $scope.option_btn_class = function(option){
            return (option.value == $scope.relative_relation) ? "btn-selected" : "";
        };
        $scope.change_option = function(option){
            $scope.relative_relation = option.value;
            $scope.update_note();
        };

        // load the similarity pairs
        $scope.load();

        $scope.current_pair = undefined;
        $scope.click_pair = function(pair){

            var request = Comparator.load(Dataset.id, pair.source.id, pair.target.id);
            if (request) {
                usSpinnerService.spin('code-spinner');
                request.then(function() {
                    usSpinnerService.stop('code-spinner');
                    $scope.source = Comparator.data.source;
                    $scope.target = Comparator.data.target;
                    $scope.diff = Comparator.data.diff;
                    $scope.note = Comparator.data.note;
                    $scope.relative_relation = Comparator.data.relative_relation;

                    $scope.current_pair = pair;

                    PR.prettyPrint();
                });
            }
        };
        $scope.highlight_row = function(pair){
            return ($scope.current_pair == pair) ? "highlight-row" : "";
        };

        $scope.update_note = function(){
            var request = Comparator.update_note($scope.source.id, $scope.target.id, $scope.relative_relation, $scope.note);
            if (request) {
                usSpinnerService.spin('note-spinner');
                request.then(function() {
                    usSpinnerService.stop('note-spinner');
                });
            }
        };

    };
    ComparatorController.$inject = [
        '$scope',
        'ScriptBrowser.services.Dataset',
        'ScriptBrowser.services.SimilarityPairs',
        'ScriptBrowser.services.Comparator',
        'usSpinnerService'
    ];
    module.controller('ScriptBrowser.controllers.ComparatorController', ComparatorController);


    module.directive('datetimeFormat', function() {
      return {
        require: 'ngModel',
        link: function(scope, element, attrs, ngModelController) {
          ngModelController.$parsers.push(function(data) {
            //convert data from view format to model format
            data = moment.utc(data, "YYYY-MM-DD HH:mm:ss");
            if (data.isValid()) return data.toDate();
            else return undefined;
          });

          ngModelController.$formatters.push(function(data) {
            //convert data from model format to view format
              if (data !== undefined) return moment.utc(data).format("YYYY-MM-DD HH:mm:ss"); //converted
              return data;
          });
        }
      }
    });

    module.directive('whenScrolled', function() {
        return function(scope, element, attr) {
            var raw = element[0];

            var checkBounds = function(evt) {
                if (Math.abs(raw.scrollTop + $(raw).height() - raw.scrollHeight) < 10) {
                    scope.$apply(attr.whenScrolled);
                }

            };
            element.bind('scroll load', checkBounds);
        };
    });

    module.directive('ngEnter', function () {
        return function (scope, element, attrs) {
            element.bind("keydown keypress", function (event) {
                if(event.which === 13) {
                    scope.$apply(function (){
                        scope.$eval(attrs.ngEnter);
                    });

                    event.preventDefault();
                }
            });
        };
    });




})();
