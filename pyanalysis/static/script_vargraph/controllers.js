(function () {
    'use strict';


    var module = angular.module('ScriptVarGraph.controllers', [
        'ScriptVarGraph.services',
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
        'ScriptVarGraph.services.Dataset'
    ];
    module.controller('ScriptVarGraph.controllers.DatasetController', DatasetController);

    var ViewController = function ($scope, Dataset, Script, usSpinnerService) {

        $scope.spinnerOptions = {
            radius: 20,
            width: 6,
            length: 10,
            color: "#000000"
        };
        $scope.current_script_id = undefined;
        $scope.script_data = undefined;
        $scope.current_type = undefined;

        $scope.set_current_script_id = function(script_id){
            $scope.current_script_id = script_id;
        };

        $scope.load_vargraph = function(script_id){
            var request = Script.load_vargraph(script_id);
            if (request) {
                usSpinnerService.spin('vis-spinner');
                request.then(function() {
                    usSpinnerService.stop('vis-spinner');
                    $scope.script_data = Script.script_data;
                });
            }

        };

        $scope.$watch('current_script_id', function (newVals, oldVals){
            if (newVals && (newVals != oldVals)){
                $scope.current_type = undefined;
                $scope.load_vargraph(newVals);
            }
        });



        $scope.highlight_class = function(){
            return ($scope.current_type) ? $scope.current_type : "";
        };

        $scope.onClicked = function(type){
            $scope.current_type = type;
            $scope.$apply();
        };



    };
    ViewController.$inject = [
        '$scope',
        'ScriptVarGraph.services.Dataset',
        'ScriptVarGraph.services.Script',
        'usSpinnerService'
    ];
    module.controller('ScriptVarGraph.controllers.ViewController', ViewController);


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
