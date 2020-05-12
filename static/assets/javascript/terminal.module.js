var terminal = angular.module("terminal", ['LocalStorageModule', 'ngRoute', 'eb.caret']);

terminal.factory('httpResponseErrorInterceptor', ['$injector', '$q', '$timeout', function($injector, $q, $timeout) {
    return {
        'responseError': function(response) {
            if (response.status === 0) {
                return $timeout(function() {
                    var $http = $injector.get('$http');
                    return $http(response.config);
                }, 2000);
            }
            return $q.reject(response);
        }
    };
}]);

terminal.config(function($httpProvider) {
    $httpProvider.interceptors.push('httpResponseErrorInterceptor');
});

terminal.config(function($routeProvider, $locationProvider) {

    $routeProvider
        .when('/:action/:inner_action/:run_cmd*', {
            template : "<terminals-window iapp='{{init_app}}' rest='{{rest}}'></terminals-window>",
            controller: function($rootScope, $scope, $routeParams, $route) {
                $scope.init_app = $routeParams.action;
                $scope.rest = $routeParams.inner_action + ' ' + decodeURIComponent($routeParams.run_cmd);
            },
            reloadOnSearch: false
        })
        .when('/:action/:inner_action', {
            template : "<terminals-window iapp='{{init_app}}' rest='{{rest}}'></terminals-window>",
            controller: function($rootScope, $scope, $routeParams, $route) {
                $scope.init_app = $routeParams.action;
                $scope.rest = $routeParams.inner_action;
            },
            reloadOnSearch: false
        })
        .when('/:action', {
            template : "<terminals-window iapp='{{init_app}}'></terminals-window>",
            controller: function($rootScope, $scope, $routeParams, $route) {
                $scope.init_app = $routeParams.action;
            },
            reloadOnSearch: false
        })
        .when('/', {
            template : '<terminals-window iapp=""></terminals-window>',
            reloadOnSearch: false
        });

    $locationProvider.html5Mode({
        enabled: true,
        requireBase: false
    });
});

terminal.run(['$route', '$rootScope', '$location', function ($route, $rootScope, $location) {

    var original = $location.path;
    $location.path = function (path, reload) {
        if (reload === false) {
            var lastRoute = $route.current;
            var un = $rootScope.$on('$locationChangeSuccess', function () {
                $route.current = lastRoute;
                un();
            });
        }
        return original.apply($location, [path]);
    };
}]);

terminal.factory('httpInterceptor', function ($q, $rootScope, $log) {
    var loadingCount = 0;

    return {
        response: function (response) {
            if(response.data && response.data.authError) {
                $rootScope.$broadcast('authError');
            }
            return response || $q.when(response);
        },

        responseError: function (response) {
            if(response.status) {
                if (response.status === 403) {
                    $rootScope.$broadcast('authError');
                }
                else if (response.status === 500) {
                    $rootScope.$broadcast('systemError');
                }
            }
            return $q.reject(response);
        }
    };
}).config(function ($httpProvider) {
    $httpProvider.interceptors.push('httpInterceptor');
});

/* Terminals Window */
terminal.directive('terminalsWindow', function() {
    return {
        templateUrl: '/templates/terminals-window',
        restrict: 'E',
        scope: {
            initWithApp: '@iapp',
            restCmd: '@rest',
        },
        link: function($scope, element, $timeout) {

            /**
             * ######################################################## LINKS
             */
            $scope.bindEvents = function() {
                $(document).on('mouseup', function(){
                    var selection = window.getSelection();
                    if(selection == 0) {
                        $scope.focusActiveTerminal();
                    }
                });

                $.ajaxSetup({
                    error: function (x, status, error) {
                        if (x.status === 403) {
                            var t = $("#term-id-"+$scope.activeTerminal).find(".holder");
                            var scp = angular.element(t).scope();
                            scp.ui.add([' ',scp.ui.dye('♦ You need to login to do that.','red')]);
                            scp.ui.addInfo('You can use <cmd>user login</cmd> command to login or <cmd>user signup</cmd> to signup imnicy.com platform.');
                        }
                    }
                });
            };

            $scope.bindEvents();
        },
        controller: function($scope, $rootScope, $timeout, localStorageService, $location) {

            /**
             * ######################################################## DEFINITIONS
             */
            $scope.terminals = [];
            $scope.playingTerminals = {};
            $scope.engine = $rootScope.engine = {};

            $scope.options = $scope.opt = $rootScope.options = $rootScope.opt = {
                //
            };


            /**
             * ######################################################## LISTENER FROM TERMINALS
             */


            /*
            $rootScope.$on('message_to_windows', function(event, data){
                term_id = data.term_id;

                if(data.action == 'setCurrentGenre') {
                    // refactor-1
                    $('#currentGenre').html("#"+data.value);
                }

                if(data.action == 'playingTrack') {
                    $scope.lastActiveTermId = term_id;
                    $scope.playingTerminals[term_id] = true;
                    $scope.isPlayingOtherTerminal();
                }

                if(data.action == 'pausedTrack') {
                    delete $scope.playingTerminals[term_id];
                    $scope.isPlayingOtherTerminal();
                }

                if(data.action == 'checkIsPlayingOtherTerminal') {
                    var vl = $scope.isPlayingOtherTerminal();
                    $rootScope.$emit('message_to_terminal', {
                        'action' : 'checkIsPlayingOtherTerminalResponse',
                        'value' : vl,
                        'term_id' : term_id
                    });
                }

                if(data.action == 'closeActiveIframe') {
                    $scope.closeActiveIframe();
                }
            });

            $scope.isPlayingOtherTerminal = function(from_terminal_perspective) {
                if($.isEmptyObject($scope.playingTerminals)) {
                    return false;
                }

                if(!$scope.playingTerminals[from_terminal_perspective||$scope.activeTerminal] || $scope.playingTerminals[from_terminal_perspective||$scope.activeTerminal] === undefined) {
                    return true;
                }

                return false;
            };

            $scope.setScWidgetFogged = function(state) {
                $timeout(function(){
                    $scope.isScWidgetFogged = state;
                    if(state == true) {
                        $scope.lastFoggedScWidgetInThisTerminal = $scope.activeTerminal;
                    } else {
                        $scope.lastFoggedScWidgetInThisTerminal = undefined;
                    }
                },1);
            };


            $scope.goToFoggedScWidget = function() {
                $scope.activeTerminal = $scope.lastActiveTermId || $scope.lastFoggedScWidgetInThisTerminal;

                $timeout(function(){
                    var hldr = $("#term-id-"+$scope.activeTerminal).find(".holder");
                    var tp = hldr.find('.sc_holder_iframe').first();

                    //if(tp > 0) {
                    //
                    //} else {
                    //	tp = -1 * tp;
                    //	tp = hldr.scrollTop() - tp;
                    //}

                    hldr.scrollTop(hldr.scrollTop() + tp.position().top - hldr.height()/2 + tp.height()/2);

                    // hldr.stop().animate({scrollTop:tp-40}, '500', function() {
                    //
                    // });
                },100);
            };
            */


            /**
             * This method closing the active iframe
             */
            $scope.closeActiveIframe = function() {
                fnd = $('.terminal-output:visible').parent().parent().find('.iframeHolder').first();
                fnd_btn = $('.iframeHolderCloseBtn').first();

                fnd_btn.fadeOut();

                fnd.fadeOut(function(){
                    fnd.html('');
                    fnd.removeClass('darkIframeBg');
                    $timeout(function(){
                        var t = $("#term-id-"+$scope.activeTerminal).find(".holder");
                        var scp = angular.element(t).scope();
                        scp.ui.addInfo('Terminated: popup');
                    },1);
                });
            };


            /**
             * This method inits app if provided
             */
            $scope.checkInit = function() {
                var t = $("#term-id-"+$scope.activeTerminal).find(".holder");
                var scp = angular.element(t).scope();

                if(!scp) {
                    $timeout($scope.checkInit, 100);
                } else {
                    if($scope.initWithApp) {
                        var m_queries = [];

                        if($scope.initWithApp.indexOf('?') !== -1) {
                            spt = $scope.initWithApp.split('?');
                            $scope.initWithApp = spt[0];
                            queries = spt[1].split('&');

                            for(var i=0,t=queries.length;i<t;i++) {
                                var query = queries[i];
                                m_queries.push(queries[i]);
                            }
                        }

                        scp.term.init(true);
                        var new_cmd = $scope.initWithApp;

                        if($scope.restCmd) {
                            var rcmd = $scope.restCmd;
                            rcmd = decodeURIComponent(rcmd);

                            rcmd = rcmd.replace('http://', '_xxPUTHTTPxx_');
                            rcmd = rcmd.replace('https://', '_xxPUTHTTPSxx_');
                            new_cmd = new_cmd + ' ' + rcmd.split('/').join(' ');
                        }

                        new_cmd = new_cmd.replace('_xxPUTHTTPxx_','http://');
                        new_cmd = new_cmd.replace('_xxPUTHTTPSxx_','https://');

                        scp.term.runCmd({
                            query: new_cmd,
                            queries: m_queries
                        });
                    } else {
                        scp.term.init();
                    }
                }
            };


            /**
             * This method inits app if provided
             */
            $scope.getTerminalsActiveAppName = function(tid) {
                var t = $("#term-id-"+tid).find(".holder");
                var scp = angular.element(t).scope();

                if(scp) {
                    var nm = angular.element(t).scope().term.preQuery;
                    return (nm?nm:'root');
                }
            };


            /**
             * This method creates a new terminal and focus to that.
             *
             * @return {void}
             */
            $scope.newTerminal = function() {
                var tid = $scope.terminals.length + 1;
                tid = tid + '-' + new Date().getTime();
                tid = tid + '_' + parseInt(Math.random() * 1000000);
                $location.path('/',false);
                $scope.activeTerminal = tid;
                $scope.terminals.push(tid);
            };


            /**
             * This method switch to terminal
             *
             * @param t {Object} Terminal object
             * @return {Boolean} true
             */
            $scope.switchTerminal = function(t) {
                $scope.activeTerminal = t;
                $scope.focusActiveTerminal();

                return true;
            };


            /**
             * This method close terminals
             *
             * @param t {Object} Terminal object
             * @return {Boolean} true
             */
            $scope.closeTerminal = function(t) {
                if(t === $scope.activeTerminal) {
                    old_index = $scope.terminals.indexOf(t);
                    $scope.terminals.splice( old_index , 1 );

                    if($scope.terminals.length > 0) {
                        if($scope.terminals[old_index - 1] !== undefined) {
                            $scope.activeTerminal = $scope.terminals[old_index - 1];
                        } else if($scope.terminals[old_index] !== undefined) {
                            $scope.activeTerminal = $scope.terminals[old_index];
                        } else if($scope.terminals[old_index + 1] !== undefined) {
                            $scope.activeTerminal = $scope.terminals[old_index + 1];
                        } else {
                            alert('off' + old_index );
                        }

                        $scope.focusActiveTerminal();
                    }
                } else {
                    $scope.terminals.splice( $scope.terminals.indexOf(t) , 1 );
                }

                return true;
            };


            /**
             * This method checks that is terminal object active.
             *
             * @param t {Object} Terminal object
             * @return {Boolean} true or false
             */
            $scope.isTerminalActive = function(t) {
                return ($scope.activeTerminal === t);
            };


            /**
             * This method focus on active terminal.
             *
             * @return {Boolean} true
             */
            $scope.focusActiveTerminal = function() {
                $timeout(function(){
                    var _the_active_terminal = $("#term-id-"+$scope.activeTerminal);
                    ti = _the_active_terminal.find(".terminal-input:visible");
                    pi = _the_active_terminal.find(".prompt-input:visible");

                    if(ti.length > 0) {
                        ti.first().focus();
                    } else if(pi.length > 0) {
                        pi.first().focus();
                    }

                    return true;
                }, 1);
            };


            /**
             * This method activates the local storage theme.
             *
             * @return {Boolean} true
             */
            $scope.setTheme = function() {
                var _the_body = $("body");
                _the_body.addClass("theme-dark");
                _the_body.css('background-size', 'cover');
            };


            /**
             * ######################################################## RUN
             */
            $scope.init = function(){
                $.ajaxSetup({ cache: false });
                $timeout(function(){
                    $scope.setTheme();
                    $scope.checkInit();
                },1);
            };

            $scope.init();
        }
    };
});


/* Terminal */
terminal.directive('terminal', function() {
    return {
        restrict: 'E',
        templateUrl: '/templates/terminal',
        scope: {
            this_term_id: '@tid'
        },
        link: function($scope, element, $timeout) {

            /**
             * ######################################################## LINKS
             */
            $scope.terminalInput = $(element).find(".terminal-input:visible").first();
            $scope.terminalOutput = $(element).find(".terminal-output:visible").first();

            $(element).on("click", "cmd", function(e) {

                var t = $(e.target);

                if(t.parent().get(0).tagName === 'CMD') {
                    t = t.parent();
                }

                t = t.text();

                if(t.indexOf('{') !== -1 && t.indexOf('}') !== -1) {
                    $scope.$apply(function() {
                        $scope.queryHistory[$scope.queryIndex] = t.replace(/({.*?})/g, '');
                    });
                } else {
                    $scope.queryHistory[$scope.queryIndex] = t;
                    $scope.term.runQuery(true);
                }
            });

            $scope.terminalInput.bind('focus', function(){
                $scope.focusedOnTerminal();
            });

            $scope.terminalInput.on('keydown', function(e) {
                $scope.term.checker(e, $scope.terminalInput);
            });

            $(window).resize(function(){
                $scope.ui.redrawTerminalInput();
                $scope.ui.redrawPromptInput();
            });
        },
        controller: function($scope, $timeout, $rootScope, $http, localStorageService, $location, $route) {
            $rootScope.$on('authError', function(){
                $scope.ui.addAuthWarning();
            });

            $rootScope.$on('systemError', function() {
                $scope.ui.addSystemWarning();
            });


            /**
             * ######################################################## DEFINITIONS
             */
            $scope.terminal = $scope.term = {}; /* This terminal object */
            $scope.engine = $rootScope.engine; /* Global engine */
            $scope.lineQueue = []; /* Queue for new lines */
            $scope.query = ""; /* Current query */
            $scope.queryHistory = []; /* History of queries */
            $scope.queryIndex = 0; /* Current query index */
            $scope.tmpQuery = undefined; /* Temporary query, pressed up button before run this query */
            $scope.helpers = {}; /* Terminal helper methods */
            $scope.ui = {}; /* Terminal ui methods */
            $scope.apps = []; /* Loaded apps */
            $scope.bitWidthChar = 16; /* Character width for non-monospaced characters like Ascii */
            $scope.bitWidthMono = 10; /* Character width for monospaced characters */
            $scope.terminalsActiveAppName = '';
            $scope.http = {}; /* Terminal data api requester */

            console.log('imnicy.com '+terminal_data.info.version+' ('+terminal_data.info.codename+') is load & ready!');


            /**
             * ######################################################## WATCHERS
             */
            $scope.$watch('term.preQuery', function(){
                $scope.ui.redrawTerminalInput();
            });

            $scope.$watch('term.prompting', function(){
                $scope.ui.redrawPromptInput();
            });

            $scope.$watchCollection('queryHistory', function(){
                if($scope.term.preQuery && $scope.queryHistory[$scope.queryIndex].indexOf($scope.term.preQuery + ' ') === 0) {
                    $scope.term.preQuery = '';
                    //$scope.queryHistory[$scope.queryIndex] = $scope.queryHistory[$scope.queryIndex].replace($scope.term.preQuery + ' ', '');
                }
            });

            $scope.keyDowns = [];

            // Event handlers
            $scope.onKeyDown = function ($event) {
                if($event.keyCode === 67 && $scope.keyDowns.indexOf(17) !== -1) {
                    $scope.term.halt();
                    $scope.keyDowns.splice($scope.keyDowns.indexOf(17), 1);
                }

                if($event.keyCode === 8) {
                    $scope.term.promptBackspaced();
                }

                if($event.keyCode === 38) { /* up */
                    $scope.term.promptChange(-1);
                    $event.preventDefault();
                }

                if($event.keyCode === 40) { /* down */
                    $scope.term.promptChange(1);
                    $event.preventDefault();
                }

                $scope.keyDowns.push($event.keyCode);
            };

            $scope.onKeyUp = function ($event) {
                fk = $scope.keyDowns.indexOf($event.keyCode);
                if(fk !== -1) {
                    $scope.keyDowns.splice(fk,1);
                }
            };


            /**
             * ######################################################## HELPERS
             */


            /**
             * This helper methods finds a shared starting word
             * from an array.
             *
             * @param A {Array} Array of strings like ['play','playlist','playlists']
             * @return {String} Returns string like 'play'
             */
            $scope.helpers.sharedStarts = function(A) {
                var tem1, tem2, s;
                var res = "";

                if (A.length === 0) return res;

                A = A.slice(0).sort();
                tem1 = A[0];
                tem2 = A.pop();

                s = tem1.length;

                while (s > 0) {
                    var m = tem1.substring(0, s);
                    var re = new RegExp("^" + m + ".*", "i");

                    if (tem2.match(re)) {
                        res = m;
                        break;
                    }--s;
                }
                return res.toLowerCase();
            };


            /**
             * This helper finds percent
             *
             * @return {String} Returns string like "---------"
             * @param dyn
             * @param total
             * @param h
             */
            $scope.helpers.getPercent = function(dyn,total,h) {
                h = (h !== undefined?h:100);
                return (h*dyn)/total;
            };


            /**
             * This helper method repeats C for N times
             * Repeating character (c parameter) for X times (n parameter).
             *
             * @param c {String} Character for repeat
             * @param n {Number} Repeat count
             * @return {String} Returns string like "---------"
             */
            $scope.helpers.repeater = function(c, n) {
                var s = "";
                for (i = 0; i < n; i++) {
                    s += c;
                }
                return s;
            };


            /**
             * This helper method scrolls terminal to bottom.
             *
             * @return {void}
             */
            $scope.helpers.scrollToBottom = function() {
                $(".holder").scrollTop(9e6);
                $scope.terminalInput.focus();
            };


            /**
             * ######################################################## INIT METHODS
             */
            $scope.term.runPreCaches = function(cb) {
                // var pres = "cmd";
                // pres = pres.split(",");
                // for(var i=0; i<pres.length; i++) {
                //     var scq = pres[i];
                //
                //     $scope.http.run(scq).then(function(response){
                //         if(response.status === 200) {
                //             /* Load app script */
                //             eval(response.data.script);
                //         }
                //         cb();
                //     });
                // }
                return cb();
            };


            /**
             * This method inits terminal
             *
             * @return {void}
             */
            $scope.term.init = function(without_header) {
                $scope.term.runPreCaches(function(){
                    $scope.ui.runLayout(true);

                    if(!without_header) {
                        var h = $scope.term.getHeader();
                        $scope.ui.add(h, function(){
                            $scope.ui.addInfo("News: "+terminal_data.news[0], "green", '📡', true);
                            $scope.ui.addInfo("Tips: "+terminal_data.tips[Math.floor(Math.random()*terminal_data.tips.length)], "yellow", '💡', true);

                            $timeout(function(){

                                xtr = $scope.ui.dye('(* '+terminal_data.info.version+', codename: '+terminal_data.info.codename+')', 'tomato');

                                $scope.ui.add([
                                    $scope.ui.br(),
                                    $scope.ui.dye('imnicy.com '+xtr+' loaded & ready to use! ', 'green'),
                                    $scope.ui.divider('-'),
                                    $scope.ui.br(),
                                    $scope.ui.dye("* Type <cmd>help</cmd> and press return to see basic commands or type <cmd>help pro</cmd> to explore:", "white")
                                ]);
                            },300);
                        });
                    } else {
                        //$scope.ui.add([$scope.ui.br(),$scope.ui.br()])
                    }
                });
            };



            /**
             * ######################################################## TERMINAL METHODS
             */


            /**
             * This method detects keyboard key press at terminal.
             * Detects key and returns related action.
             *
             * @param e {Element} Keyboard keypress event
             * @return {void}
             */
            $scope.term.checker = function(e) {
                if($scope.listeningKeys !== undefined) {

                    var found = -1;

                    angular.forEach($scope.listeningKeys, function(value, key){
                        if(e.keyCode === value.code) {
                            found = e.keyCode;
                            //$scope.listeningKeys = undefined;
                            value.action();

                            if(value.code === 13) {
                                e.preventDefault();
                            }
                        }
                    });

                    if(found === 13) {
                        e.preventDefault();
                        return;
                    }

                }

                if($scope.queryIndex !== $scope.queryHistory.length - 1 && e.keyCode !== 38 && e.keyCode !== 40 && e.keyCode !== 13) {
                    var fnd = $scope.queryHistory[$scope.queryIndex];
                    $scope.queryIndex = $scope.queryHistory.length - 1;
                    $scope.queryHistory[$scope.queryIndex] = fnd;
                }

                switch (e.keyCode) {
                    case 13:
                        /* Enter */
                        e.preventDefault();
                        $scope.term.runQuery();
                        break;
                    case 8:
                        /* Backspace */
                        $scope.term.backspaced();
                        break;
                    case 38:
                        /* Arrow up */
                        e.preventDefault();
                        $scope.term.changeQuery(1);
                        break;
                    case 40:
                        /* Arrow down */
                        e.preventDefault();
                        $scope.term.changeQuery(-1);
                        break;
                    case 27:
                        /* ESC */
                        e.preventDefault();
                        $scope.term.closeIframe();
                        break;
                    case 9:
                        /* Tab */
                        e.preventDefault();
                        $scope.term.autoCompleteQuery(e);
                        break;
                    case 67:
                        /* Ctrl+C */
                        if (e.ctrlKey) {
                            $scope.term.terminatePreQuery(true, false);
                        }
                        break;
                }
            };

            $scope.term.halt = function() {
                if($scope.term.preQuery) {
                    $scope.term.terminatePreQuery();
                }

                if($scope.term.prompting) {
                    $scope.term.terminatePrompt();
                }
            };

            $scope.term.closeIframe = function() {
                $scope.term.sendWindows('closeActiveIframe');
            };

            $scope.term.sendWindows = function(action,value) {
                $rootScope.$emit('message_to_windows', {
                    'term_id' : $scope.this_term_id,
                    'action' : action,
                    'value' : value
                });
            };

            $rootScope.$on('message_to_terminal', function(event, data){

                if(data.term_id === $scope.this_term_id) {
                    if(data.action === 'checkIsPlayingOtherTerminalResponse') {
                        $scope.term.otherTerminalIsAlreadyPlaying = data.value;
                    }

                    if(data.action === 'addHeader') {
                        var h = $scope.term.getHeader();
                        $scope.ui.add(h);
                    }
                }
            });

            $timeout(function(){
                if(_run_cmd_ !== "") {
                    $scope.term.runCmd({
                        query: _run_cmd_,
                        remove_pre_query: true
                    });
                }
            },300);


            /**
             * This function checks backspace position to exit pre-query.
             */
            $scope.term.backspaced = function() {
                if($scope.term.preQuery && $scope.caretPosition.get === 0) {
                    $scope.term.terminatePreQuery();
                }
            };


            /**
             * This function checks backspace position to exit prompt.
             */
            $scope.term.promptBackspaced = function() {
                //console.log('$scope.term.prompting:' + $scope.term.prompting +' , $scope.promptCaretPosition.get: '+$scope.promptCaretPosition.get + ',  $scope.term.promptAnswer: ' + $scope.term.promptAnswer)
                if($scope.term.prompting && (($scope.promptCaretPosition.get === 0 && ($scope.term.promptAnswer === '' || $scope.term.promptAnswer === undefined)) || $scope.promptCaretPosition.get === undefined)) {
                    $scope.term.terminatePrompt();
                }
            };


            /**
             * This function checks up/down keys of prompt.
             */
            $scope.term.promptChange = function(p) {
                if(p!==undefined) {
                    if(p > 0) { /* +1 */
                        if($scope.term.promptAnswers && $scope.term.promptAnswers.length > 0) {
                            if($scope.term.promptAnswersIndex + 1 <= $scope.term.promptAnswers.length - 1) {
                                $scope.term.promptAnswersIndex++;
                            }
                        }
                    } else {    /* -1 */
                        if($scope.term.promptAnswers && $scope.term.promptAnswers.length > 0) {
                            if($scope.term.promptAnswersIndex - 1 >= 0) {
                                $scope.term.promptAnswersIndex--;
                            }
                        }
                    }
                }

                if($scope.term.promptAnswers && $scope.term.promptAnswersIndex !== undefined) {
                    $scope.term.promptAnswer = $scope.term.promptAnswers[$scope.term.promptAnswersIndex];
                }
            };


            /**
             * This function terminates pre-query.
             */
            $scope.term.terminatePreQuery = function(delete_everything, with_message=true) {
                $scope.terminatedApp = $scope.term.preQuery + '';
                $location.path('/', false);
                $scope.term.preQuery = undefined;

                if (with_message) {
                    $scope.ui.addInfo('Terminated app: ' + $scope.terminatedApp);
                }

                if(delete_everything) {
                    $timeout(function(){
                        $scope.queryIndex = $scope.queryHistory.length;
                        $scope.queryHistory[$scope.queryIndex] = '';
                    },1);
                }
            };


            /**
             * This function terminates pre-query.
             */
            $scope.term.clear = function() {

                $scope.queryHistory[$scope.queryIndex] = '';

                $('.terminal-output').find('.line').remove();
            };


            /**
             * This function terminates prompt.
             */
            $scope.term.terminatePrompt = function(silent) {

                $scope.term.prompting = undefined;
                $scope.term.promptingPassword = undefined;
                $scope.term.promptAnswer = undefined;
                $scope.term.promptAnswers = undefined;
                $scope.term.promptAnswersIndex = undefined;

                if(!silent) {
                    $scope.ui.addInfo('Terminated module: prompt');
                }

                $timeout(function(){ $scope.ui.redrawTerminalInput(); },1);
            };


            /**
             * This method changes the query by keyboard commands such as UP and DOWN.
             * Checks the commands history ($scope.queryHistory) and
             * navigate in array with up and down keys.
             *
             * @param up_or_down {Number} Up or down integer. 1 is up and -1 is down.
             * @return {void}
             */
            $scope.term.changeQuery = function(up_or_down) {

                $timeout(function(){
                    if (up_or_down > 0) { /* up */
                        $scope.queryIndex = ($scope.queryIndex > 0) ? ($scope.queryIndex - 1) : 0;
                    } else { /* down */
                        $scope.queryIndex = ($scope.queryIndex < $scope.queryHistory.length - 1) ? ($scope.queryIndex + 1) : $scope.queryHistory.length - 1;
                    }

                    if($scope.term.preQuery && $scope.term.preQuery !== '' && $scope.queryHistory[$scope.queryIndex].indexOf($scope.term.preQuery + ' ')===0) {
                        $scope.queryHistory[$scope.queryIndex] = $scope.queryHistory[$scope.queryIndex].replace($scope.term.preQuery + ' ', '');
                    }
                },1);
            };


            /**
             * This method finds cached app and if found
             *
             * @return {String}
             */
            $scope.term.findCachedApp = function(command) {

                if (command === undefined || command === "") {
                    return false;
                }

                console.log("Searching command from cached apps: " + command);

                var app_found = false;

                /* First, search loaded apps by name.. */
                if($scope.apps[command] !== undefined && $scope.apps[command].caching === true) {

                    console.log("Found status (true): " + command);
                    return command;
                }

                /* ..then search in loaded app by their aliases.. */
                Object.keys($scope.apps).forEach(function(e){

                    if(!app_found) {
                        var this_app = $scope.apps[e];

                        if (this_app.caching === false) {
                            return ;
                        }

                        var this_app_aliases = this_app.aliases;

                        var search_aliases = [];

                        this_app_aliases.forEach(function(e){
                            search_aliases.push(e.trim());
                        });

                        if(command === "help" && this_app.name === "help") {
                            app_found = this_app.name;
                        } else {
                            if(search_aliases.indexOf(command) !== -1) {
                                app_found = this_app.name;
                            }
                        }

                        // Check commands

                        // console.log(this_app.commands);
                        //
                        // Object.keys(this_app.commands).forEach(function(ex){
                        //     console.log(ex + " - " + command);
                        //
                        //     if(!app_found && ex == command) {
                        //         app_found = this_app.name;
                        //     }
                        // });
                    }
                });

                console.log("Found status: " + app_found);
                return app_found;
            };


            /**
             * This method gets current command and forwards it to the /api/run method
             * via http get request. API returns a script or empty response.
             *
             * @return {void}
             */
            $scope.term.runQuery = function(ignore_pre_query, cb) {

                var query = $scope.queryHistory[$scope.queryIndex];

                if (query === undefined) {
                    query = '';
                }

                $scope.query = query;

                if($scope.query === 'clear') {
                    return $scope.term.clear();
                }

                if($scope.listeningRunQuery !== undefined) {

                    $timeout(function() {
                        $scope.queryHistory[$scope.queryIndex] = '';
                        $scope.listeningRunQuery = undefined;
                    }, 100);

                    return $scope.listeningRunQuery(query);
                }

                var split_query = query.split(" ");

                if(!ignore_pre_query && $scope.term.preQuery) {

                    if($scope.query === 'exit') {
                        return $scope.term.terminatePreQuery(true);
                    }

                    $scope.ui.runCmd();

                    if(!query) {
                        return;
                    }

                    var command = $scope.term.preQuery;

                } else {

                    $scope.ui.runCmd();

                    if(!query) {
                        return;
                    }

                    command = split_query[0];

                    $scope.term.preQuery = '';
                }


                var app_name = $scope.term.findCachedApp(command);

                /* ..not found? get it from webservice */
                if(!app_name) {

                    var pq = '';

                    if($scope.term.preQuery) {
                        pq = $scope.term.preQuery + ' ';
                    }

                    var scq = pq + $scope.query;

                    if(scq) {
                        scq = scq.toLowerCase();
                    }
                    else {
                        return ;
                    }

                    $scope.http.run(scq).then(function(response){
                        if(response.status === 200) {
                            var data = response.data;
                            var app_name = $scope.term.findCachedApp(data.app.name);

                            if(!app_name) {
                                /* Load app script */
                                eval(data.script);

                                $timeout(function(){
                                    if(data.app !== undefined && data.app !== null) {

                                        var aliases_not_starting = !!(data.app.aliases && data.app.aliases.indexOf(command) === -1);

                                        if($scope.query.toLowerCase().indexOf(data.app.name) !== 0 && aliases_not_starting && (!$scope.term.preQuery || $scope.term.preQuery === '')) {
                                            $scope.ui.add($scope.ui.br(), function(){
                                                $scope.ui.addInfo('Initializing app: ' + data.app.name);
                                                $scope.term.preQuery = data.app.name;
                                            });
                                        }

                                        app_name = data.app.name;

                                        /* Run the query */
                                        $scope.term.runApp(app_name, ignore_pre_query);

                                        if(cb) {
                                            cb(true);
                                        }
                                    }
                                },500);
                            } else {
                                $scope.queryHistory[$scope.queryIndex] = app_name + " " + scq, ignore_pre_query;
                                return $scope.term.runQuery(false, function(status) {

                                });
                            }
                        } else {
                            $scope.term.returnError();
                        }
                    });
                } else {
                    /* Run the query */

                    $scope.term.runApp(app_name, ignore_pre_query);

                }

                $timeout(function(){
                    $scope.queryIndex++;
                    $scope.queryHistory[$scope.queryIndex] = '';
                    localStorageService.set('queryHistory', $scope.queryHistory);
                    localStorageService.set('queryIndex', $scope.queryIndex);
                },1);

            };


            /**
             *
             */
            $scope.focusedOnTerminal = function() {

            };


            /**
             * This method execute apps active command.
             *
             * @return {void}
             */
            $scope.term.runApp = function(app_name, ignore_pre_query) {

                qr = ($scope.term.preQuery ? $scope.term.preQuery+' ' : '') + $scope.query;

                var cmds = qr.split(' ');
                var ctl_arguments = [];

                if(cmds.length >= 3) {
                    ctl_arguments = cmds.slice(2);
                }

                if(!ignore_pre_query && $scope.term.preQuery !== app_name) {
                    $scope.term.preQuery = app_name;
                }

                var scp_app = "$scope.apps." + app_name;

                try {
                    var vvv = scp_app+".controller('"+qr+"')";
                    eval(vvv);
                } catch (e) {
                    return ;
                }

                //$location.path('/'+app_name, false);

                $timeout(function(){
                    var app_commands = eval("$scope.apps."+app_name+".commands");
                    var cmd = cmds[1] || 'index';

                    var all_aliases_arr = [];
                    for(var key in app_commands){

                        var run_eval = false;
                        var real_cmd = null;

                        if(key === cmd.toLowerCase()) {
                            real_cmd = cmd;
                        }
                        else if(app_commands[key]['aliases'] && app_commands[key]['aliases'].indexOf(cmd.toLowerCase()) !== -1) {
                            real_cmd = key;
                        }

                        if (real_cmd !== null) {
                            var app_scope_part = "$scope.apps."+app_name+".commands."+real_cmd;
                            var run_eval_arguments = eval(app_scope_part+".arguments");
                            for (argument in run_eval_arguments) {
                                if (run_eval_arguments[argument].substr(-1, 1) === '?') {
                                    run_eval_arguments.splice(argument, 1)
                                }
                            }

                            var run_eval_first_part = app_scope_part+".init";

                            if (run_eval_arguments.length > ctl_arguments.length) {
                                $scope.ui.add([
                                    $scope.ui.divider("-"),
                                    $scope.ui.dye("☹ You have a arguments problem, use <cmd>help app " + app_name + " " + cmd + "</cmd> to view details.", "red")
                                ]);
                                return ;
                            }

                            ctl_arguments = "'"+ctl_arguments.join('\',\'')+"'";
                            run_eval = run_eval_first_part + "("+ctl_arguments+")";
                        }

                        if(run_eval) {
                            return eval(run_eval);
                        }
                    }

                    var qrz = $scope.query.split(' ');

                    if($scope.term.preQuery && isNaN(qrz[qrz.length-1])) {
                        return $scope.term.searchGlobally();
                    }
                }, 100);
            };

            $scope.term.searchGloballyCount = 1;

            $scope.term.searchGlobally = function() {
                if($scope.term.searchGloballyCount <= 0) {
                    $scope.term.searchGloballyCount = 1;
                    return;
                }

                if($scope.query) {
                    nq = $scope.query.replace($scope.term.preQuery+' ','');
                    $scope.ui.addWarning('Command not found in current app ('+$scope.term.preQuery+'), searching globally with cmd: <cmd>'+nq+'</cmd>');
                }
            };


            /**
             * This method executes cmd.
             *
             * @return {void}
             */
            $scope.term.runCmd = function(o) {
                var def_opts = {
                    query: null,
                    remove_pre_query: false,
                    return_to_old_query: false,
                    add_to_history: true,
                    queries: null
                };

                var opts = $.extend({}, def_opts, o);
                var qr = opts.query;

                if(opts.return_to_old_query) {
                    $scope.term.terminatePreQuery();
                }

                if(opts.remove_pre_query === true) {
                    $scope.term.preQuery = '';
                    console.log('Removed pre query');
                }

                if(opts.queries != null && opts.queries.length > 0) {
                    qr += ' -' + opts.queries.join(' -');
                }

                $scope.queryHistory[$scope.queryIndex] = qr;

                if(opts.return_to_old_query && typeof $scope.terminatedApp != 'undefined') {
                    $scope.term.runQuery(false, function(status){
                        $timeout(function(){
                            $scope.ui.add('Switching back to app: '+$scope.terminatedApp);
                            $scope.term.preQuery = $scope.terminatedApp;
                        },1);
                    });
                } else {
                    $scope.term.runQuery();
                }

                if(!opts.add_to_history) {
                    $scope.queryHistory.pop();
                    $timeout(function(){
                        $scope.queryHistory.push('');
                    },1);
                }
            };

            $scope.term.mergePreQuery = function($event){
                if($scope.term.preQuery && $scope.term.preQuery.length > 0) {
                    $scope.queryHistory[$scope.queryIndex] = $scope.term.preQuery + ' ' + $scope.queryHistory[$scope.queryIndex];
                    $scope.term.preQuery = '';
                }
            };


            /*
             * This method returns something went wrong message
             *
             * @return {String} Something went wrong, please try again..
             */
            $scope.term.returnError = function(error_code, error_message) {
                var m = 'Something went wrong, please try again..';

                if(error_code === 302) {
                    m = "☉ Validation failed with error message: "+error_message;
                }

                if(error_code === 404) {
                    m = "☉ I'm sorry Dave, command not found. You can Google it with this cmd: <cmd>cmd search "+$scope.query+"</cmd>";
                }

                if(error_code === 5404) {
                    m = [
                        $scope.ui.divider("-"),
                        $scope.ui.dye("☉ App is not found. For help, please use 'help pro' command.", 'red')
                    ];
                }

                if(error_code === 4404) {
                    m = [
                        $scope.ui.divider("-"),
                        $scope.ui.dye("☉ App found but command is not found. For help, please use 'help {app_name}' command.", 'red'),
                        "For example: If you need a help with 'cmd' app, try this command:",
                        "<cmd>help app cmd</cmd>"
                    ];
                }

                if(error_code === 2404) {
                    m = [
                        $scope.ui.divider("-"),
                        $scope.ui.dye("☹ You have connection problems.", 'red'),
                        "Maybe some of our services is blocked from your country.",
                        "You can always use VPN by using this command:",
                        "<cmd>vpn</cmd>"
                    ];
                }

                if(typeof error_code == 'string') {
                    m = [
                        $scope.ui.divider("-"),
                        $scope.ui.dye("☹ "+error_code, 'red'),
                    ];
                }

                if(typeof m == 'string') {
                    $scope.ui.addLine($scope.ui.dye(m, 'red'));
                } else {
                    $scope.ui.add(m);
                }

            };


            $scope.term.getQueryLevel = function(query) {
                var qs = query.split(' ');
                return qs.length;
            };


            /*
             * This method autocompletes the input field.
             *
             * @return {Boolean} false
             */
            $scope.term.autoCompleteQuery = function(e) {
                e.preventDefault();

                var query = ($scope.term.preQuery && $scope.term.preQuery.length > 0 ? $scope.term.preQuery + ' ':'') + $scope.queryHistory[$scope.queryIndex];
                var cmds = query.split(' ');
                var total_level = $scope.term.getQueryLevel(query);
                var total_i = 0;
                var text = '';

                while (total_i < total_level) {
                    var ret = [];

                    if(total_level === 1) {
                        app_or_cmd = query.toLowerCase();
                        pr = '';
                    } else {
                        app_or_cmd = cmds[total_i].toLowerCase();
                        var prev = [];

                        for(var zz=0,tt=total_i;zz<tt;zz++) {
                            prev.push(cmds[zz]);
                        }

                        pr = prev.join(' ') + ' ';
                    }

                    for(var key in app_commands) {
                        /* App level */
                        if(total_level === 1) {
                            if(key.toLowerCase().indexOf(app_or_cmd) === 0 && ret.indexOf(key) === -1) {
                                ret.push(pr+key);
                            }

                            if(app_commands[key].aliases) {
                                for(var i=0,t=app_commands[key].aliases.length;i<t;i++) {
                                    if(app_commands[key].aliases[i].toLowerCase().indexOf(app_or_cmd) === 0 && ret.indexOf(app_commands[key].aliases[i]) === -1) {
                                        ret.push(pr+app_commands[key].aliases[i]);
                                    }
                                }
                            }
                        }

                        /* Cmd level */
                        for(var xkey in app_commands[key].commands) {
                            if(xkey.toLowerCase().indexOf(app_or_cmd) === 0 && ret.indexOf(xkey) === -1) {
                                ret.push(pr+xkey);
                            }

                            if(total_level > 1) {
                                if(app_commands[key].commands[xkey].i) {
                                    var cdx = app_commands[key].commands[xkey].i;

                                    for(var zk in cdx) {
                                        var cdd = cdx[zk].collection_data;

                                        if(cdd) {
                                            for(var ax=0,axt=cdd.length;ax<axt;ax++) {
                                                if(cdd[ax].toLowerCase().indexOf(app_or_cmd) === 0 && ret.indexOf(cdd[ax]) === -1 ) {
                                                    ret.push(pr+cdd[ax]);
                                                }
                                            }
                                        }
                                    }
                                }
                            }
                        }
                    }

                    total_i++;
                }

                $scope.suggestions = ret;

                $scope.$apply(function() {
                    if($scope.suggestions.length > 1) {
                        var shared_starts = $scope.helpers.sharedStarts($scope.suggestions);

                        if(shared_starts.length > 0) {
                            if($scope.term.preQuery) {
                                $scope.queryHistory[$scope.queryIndex] = shared_starts.replace($scope.term.preQuery+' ','');
                            } else {
                                $scope.queryHistory[$scope.queryIndex] = shared_starts;
                            }
                        } else {
                            //$scope.queryHistory[$scope.queryIndex] = shared_starts;
                        }

                        $scope.ui.add($scope.suggestions.join('&nbsp;&nbsp;&nbsp;&nbsp;'));
                    } else if($scope.suggestions.length === 1) {
                        if($scope.term.preQuery && $scope.suggestions.length > 0) {
                            $scope.queryHistory[$scope.queryIndex] = $scope.suggestions[0].replace($scope.term.preQuery+' ','');
                        } else {
                            $scope.queryHistory[$scope.queryIndex] = $scope.suggestions[0];
                        }
                    }
                });

                // console.log('ac: ' , query);
                return false;
            };


            /**
             * This method returns terminal header string
             *
             * @return {String} Terminal header defined at function
             */
            $scope.term.getHeader = function() {

                var logo = [
                        $scope.ui.dye(" _ _ _        __  _   _  __  ","white"),
                        $scope.ui.dye("| | | |_||   / _|| \\_/ ||  \\ ","white"),
                        $scope.ui.dye("| V V /o\\o\\ ( (_ | \\_/ || o )","white"),
                        $scope.ui.dye(" \\_n_/\\(|_() \\__||_| |_||__/ ","white"),
                        $scope.ui.dye("                             ","white")
                    ];

                var msg = [
                    $scope.ui.divider('-'),
                    $scope.ui.br(),
                    $scope.ui.dye("Hello, welcome to imnicy.com! imnicy.com is an internet operating system based on command-line interface.", "green"),
                    $scope.ui.br()
                ];
                return_data = logo.concat(msg);
                return [$scope.ui.br()].concat(return_data);
            };

            $scope.ui.runLayout = function(silent) {
                if(window.localStorage['layout_data']) {
                    var layout = JSON.parse(window.localStorage['layout_data']);

                    if(!silent) {
                        $scope.ui.addWarning('Layout set: ' + layout.name);
                    }

                    $scope.ui.setLayout(layout,silent);
                } else {
                    $scope.ui.setLayout(false);
                }
            };

            $scope.ui.setLayout = function(layout, silent) {
                var _the_bg = $('#bg');

                if(layout) {
                    if(!silent) {
                        $scope.ui.addInfo('Preloading layout image, please wait..');
                    }

                    _the_bg.css("background-size", "cover");
                    _the_bg.css("background-image", "url("+layout.image+")");
                    _the_bg.addClass('active');

                    $('#curtain').addClass('active');
                } else {
                    _the_bg.css("background-image", "none");
                    _the_bg.addClass('active');

                    $('#curtain').addClass('active');
                    return $("body").css('background', 'none');
                }
            };


            /**
             * ######################################################## UI METHODS
             */


            /**
             * This ui method repeats dash character and add it to terminal
             * You can imagine it like <hr> tag on html
             *
             * @return {String} "-" repeated 1000 times
             */
            $scope.ui.divider = $scope.ui.hr = function(chr) {

                chr = '-';

                if(chr) {
                    var char = chr;
                    var w = $scope.bitWidthMono;
                } else {
                    var char = '▋';
                    var w = $scope.bitWidthChar;
                }

                var count = $('body').outerWidth()/* / (w)*/;
                return "<div class='divider'>" +
                    $scope.helpers.repeater(char, Math.ceil(count) ) + "</div>";
            };


            /**
             * This ui method generates a box
             *
             * @return {String} Box
             */
            $scope.ui._box = function(title) {
                var count = ($(window).outerWidth() - 20) / (10);
                var b = [];

                if(title !== undefined) {
                    b.push("┌──[ "+title+" ]"+$scope.helpers.repeater('─', count-(7+title.length) )+"┐ ");
                } else {
                    b.push("┌"+$scope.helpers.repeater('─', count-3 )+"┐ ");
                }

                b.push("│  * Hello! Welcome to imnicy.com"+$scope.helpers.repeater(' ', count-32 )+"│▒");
                b.push("│    You can subscribe by using 'subscribe' command! │▒");
                b.push("╞═╤═════╤═══════════╡▒");
                b.push("│ ├──┬──┤           │▒");
                b.push("│ └──┴──┘           │▒");
                b.push("└───────────────────┘▒");
                b.push(" ▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒▒");
                b.push("					            ");

                return b;
            };

            $scope.ui.box = function() {
                $scope.ui.add($scope.ui._box('Naber'));
            };


            /**
             * This ui method creates header with dashes
             * @param title {String} Header title, for example: Music
             * @return {String} Returns "---[ Music ]-----------------------------"
             */
            $scope.ui.listHeader = function(title) {
                var ntitle = title.split(':');

                if(ntitle.length === 1) {
                    ntitle = ntitle[0];
                } else {
                    ntitle = ntitle[0] + " <span class='dyer-white'>("+ntitle[1]+")</span>";
                }

                var begin = $scope.helpers.repeater('-', 3) + " <span class='dyer-yellow'>" + ntitle + "</span> ";

                return "<div class='divider dyer-yellow'>" +
                    begin +
                    $scope.helpers.repeater('-', 99999 ) + "</div>";
            };


            /**
             * This method returns a progressbar component.
             * @return {String} Returns like "......."
             */
            $scope.ui._progressBar = function(color) {
                return '<span style="color:'+color+';width:'+$scope.bitWidthMono+'px;overflow:hidden;">.</span>'
            };


            $scope.ui.progressBar = function(playing_percent, loading_percent) {
                var count = $('body').outerWidth() / $scope.bitWidthMono;
                var playing_percent_calc = (count * playing_percent) / 100;
                var loading_percent_calc = (count * loading_percent) / 100;

                count = Math.ceil(count);
                playing_percent_calc = Math.ceil(playing_percent_calc);
                loading_percent_calc = Math.ceil(loading_percent_calc);

                return "<div class='divider clickToSkip' style='cursor:pointer;'>" +
                    $scope.helpers.repeater($scope.ui._progressBar('white'), Math.ceil(playing_percent_calc)) +
                    $scope.helpers.repeater($scope.ui._progressBar('#51C252'), Math.ceil(loading_percent_calc - playing_percent_calc)) +
                    $scope.helpers.repeater($scope.ui._progressBar('#333'), Math.ceil((count - (loading_percent_calc))) ) +
                    "</div>";
            };


            /**
             * This method adds colored text to terminal
             * Current colors: green, orange, white
             *
             * @param text {String} Text for coloring
             * @param color
             * @return {[]|String} Returns div tag with color class
             */
            $scope.ui.dye = function (text, color) {
                if(typeof text == 'array' || typeof text == 'object') {
                    var return_array = [];
                    text.forEach(function(i){
                        return_array.push("<span class='dyer-" + color + "'>" + text[i] + "</span>");
                    });
                    return return_array;
                } else {
                    return "<span class='dyer-" + color + "'>" + text + "</span>";
                }
            };


            /**
             * This method adds break line to terminal
             * @return {string}
             */
            $scope.ui.br = function() {
                return "<br>";
            };


            /**
             * This method adds break half to terminal
             * @return {string}
             */
            $scope.ui.halfBr = function() {
                return "<div style='height:5px;float:left;width:10px;display:block'></div>";
            };


            /**
             *
             */
            $scope.ui.runCmd = function() {
                if($scope.term.preQuery) {
                    ppart = $scope.term.preQuery;
                    qpart = $scope.query.replace($scope.term.preQuery+' ','');
                } else {
                    qs = $scope.query.split(' ');
                    ppart = qs.shift();
                    qpart = qs.join(' ');
                }

                return $scope.ui.add([$scope.ui.br(), $scope.ui.dye('$ '+ppart+' <span class="qry">'+qpart+'</span><span>↵</span>','runcmd-green'), $scope.ui.br()]);
            };

            $scope.ui.windowOpen = function(url, cb) {
                var newWin = window.open(url);

                if(!newWin || newWin.closed || typeof newWin.closed=='undefined')
                {
                    $scope.ui.addError('New window is blocked, you can re-run same command or give access for popups (we never open spam popups). Or, simply click this link instead: <a href="'+url+'" target="_blank">'+url+'</a>');
                }
            };


            /**
             * This method opens iframe
             * @return {void}
             */
            $scope.ui.iframe = function(url, cb) {
                fnd = $('.terminal-output:visible').parent().parent().find('.iframeHolder').first();
                fnd_btn = $('.iframeHolderCloseBtn').first();

                fnd.fadeIn(function(){
                    fnd_btn.delay(1000).fadeIn(function(){
                        fnd.html('<iframe src="'+url+'" scrolling="no" id="ttt_iframe"></iframe>');

                        fnd.addClass('darkIframeBg');

                        $('.terminal-input:visible').blur();

                        var iframe = $("#ttt_iframe")[0];
                        iframe.contentWindow.focus();

                        if(cb) {
                            return cb();
                        }
                    });
                });

                //$scope.ui.addLine('<iframe width="100%" height="100%" src="'+url+'"></iframe>');
            };


            /**
             * This method adds new line to terminal and fade in
             *
             * @param str {String} New line string
             * @return {void}
             */
            $scope.ui.addLine = function(str) {
                var tpl = $("<pre>").html(str).addClass("line");

                $scope.terminalOutput.append(tpl);
                // tpl.fadeIn(360);

                $scope.helpers.scrollToBottom();
            };


            /**
             *
             */
            $scope.ui.redrawTerminalInput = function() {
                $timeout(function(){
                    var ww = $(window).width();
                    var pqw = $('.terminal-input:visible').parent().find('.pre-query').first().outerWidth();
                    $scope.terminalInput.css('width', ww - pqw - 40);
                    $scope.terminalInput.focus();
                },10);
            };

            $scope.ui._redrawPromptInput = function() {
                var ww = $(window).width();
                var pqw = $('.prompt-input:visible').parent().find('.pre-prompt').first().outerWidth();
                $('.prompt-input:visible').first().css('width', ww - pqw - 40);
                $('.prompt-input:visible').first().focus();
            };

            $scope.ui.redrawPromptInput = function() {
                $timeout($scope.ui._redrawPromptInput,10);
                $timeout($scope.ui._redrawPromptInput,500);
                $timeout($scope.ui._redrawPromptInput,3000);
            };


            /**
             * This method clears the terminal.
             *
             * @return {void}
             */
            $scope.ui.clear = function(app_name) {
                $scope.terminalsActiveAppName = app_name;

                $scope.terminalOutput.find("pre.line").each(function(t){
                    var ts = $(this);
                    var toa = setTimeout(function() {
                        ts.fadeOut(50);
                        $scope.helpers.scrollToBottom();
                    }, 10 * t);
                });
            };


            /**
             * This method adds multiple lines to terminal.
             * If terminal is busy, it'll retry in 300 ms
             *
             * @param obj {string} String or string array
             * @param callback
             * @param tms
             * @return {boolean}
             */
            $scope.ui.add = function(obj, callback, tms) {

                if ($scope.lineQueue.length > 0) {
                    $timeout(function() {
                        $scope.ui.add(obj, callback, tms);
                    }, 450);

                    return false;
                }

                if (typeof obj == "object") {
                    obj.forEach(function(e, t) {

                        if(tms < 10) {
                            $scope.ui.addLine(e);
                            $scope.lineQueue.splice($scope.lineQueue.indexOf(to), 1);
                            if(callback !== undefined && $scope.lineQueue.length === 0) {
                                callback();
                            }
                        } else {
                            var to = $timeout(function() {
                                $scope.ui.addLine(e);
                                $scope.lineQueue.splice($scope.lineQueue.indexOf(to), 1);
                                if(callback !== undefined && $scope.lineQueue.length === 0) {
                                    callback();
                                }
                            }, (tms||(42/3, 10)) * t);

                            $scope.lineQueue.push(to);
                        }
                    });
                } else {
                    $scope.ui.addLine(obj);
                    if(callback !== undefined && $scope.lineQueue.length === 0) {
                        callback();
                    }
                }
            };


            /**
             * This method adds YES/NO question.
             *
             * @return {void}
             */
            $scope.ui.addYNQuestion = function(s,easy,cb) {
                return $scope.ui.ask(s,easy,cb);
            };


            /**
             * This method adds prompt.
             *
             * @return {void}
             */
            $scope.answerPrompt = function() {
                if($scope.term.promptCb) {
                    $scope.term.promptCb($scope.term.promptAnswer);
                }

                $scope.term.terminatePrompt(true);
            };

            $scope.ui.prompt = function(s,password_field,value,cb) {
                $timeout(function(){
                    var dc = 'orange';

                    $scope.term.prompting = s;
                    $scope.term.promptingPassword = !!password_field;
                    $scope.term.promptCb = cb;

                    if(value) {
                        if(typeof value == 'object') {
                            $scope.term.promptAnswers = value[1];
                            $scope.term.promptAnswersIndex = value[1].indexOf(value[0])||0;

                            $scope.term.promptChange();
                        } else {
                            $scope.term.promptAnswer = value;
                        }
                    }

                    $timeout(function(){
                        $scope.ui.redrawPromptInput();
                    },1);
                },1);
            };


            $scope.ui.ask = function(s,easy,cb) {
                $timeout(function(){

                    q = (easy===true)?'(Y/n)':'(y/N)';
                    var dc = 'orange';

                    $scope.term.prompting = s + q;
                    $scope.term.promptingPassword = false;
                    $scope.term._promptCb = cb;

                    $scope.term.promptCb = function(){
                        resp = $scope.term.promptAnswer;
                        if((resp !== undefined && resp.toLowerCase() == 'y') || ((resp == '' || resp === undefined) && easy === true)) {
                            return $scope.term._promptCb(true);
                        } else {
                            return $scope.term._promptCb(false);
                        }
                    };

                    $timeout(function(){
                        $scope.ui.redrawPromptInput();
                    }, 1);
                }, 1);
            };


            /**
             * This method adds information.
             *
             * @return {void}
             */
            $scope.ui.addAuthWarning = $scope.ui.addLogin = function() {

                warn_sign = [];

                warn_sign.push($scope.ui.br());
                warn_sign.push($scope.ui.divider('*'));
                warn_sign.push($scope.ui.br());
                warn_sign.push($scope.ui.dye(' ad8888888888ba                                   ', 'yellow'));
                warn_sign.push($scope.ui.dye('dP`         `"8b,                                 ', 'yellow'));
                warn_sign.push($scope.ui.dye('8  ,aaa,       "Y888a     ,aaaa,     ,aaa,  ,aa,  ', 'yellow'));
                warn_sign.push($scope.ui.dye('8  8` `8           "8baaaad""""baaaad""""baad""8b ', 'yellow'));
                warn_sign.push($scope.ui.dye('8  8   8              """"      """"      ""    8b', 'yellow'));
                warn_sign.push($scope.ui.dye('8  8, ,8         ,aaaaaaaaaaaaaaaaaaaaaaaaddddd88P', 'yellow'));
                warn_sign.push($scope.ui.dye('8  `"""`       ,d8""                              ', 'yellow'));
                warn_sign.push($scope.ui.dye('Yb,         ,ad8"    '+$scope.ui.dye('RESTRICTED MEMBERS-ONLY COMMAND!','white')+'            ', 'yellow'));
                warn_sign.push($scope.ui.dye(' "Y8888888888P"      '+$scope.ui.dye('You need to login or signup to run that command.','orange')+'                         ','yellow'));

                $scope.ui.add(warn_sign, function(){
                    infos = [$scope.ui.br()];
                    infos.push($scope.ui.dye('You have entered a command that is only available to imnicy.com members!','white'));
                    infos.push($scope.ui.dye('You can simply login with <cmd>user login</cmd> command. You can always sign up by entering <cmd>user signup</cmd> command.','green'));
                    infos.push($scope.ui.dye('','green'));
                    $scope.ui.add(infos);
                });
            };


            /**
             * This method add system error message
             *
             * @returns {void}
             */
            $scope.ui.addSystemWarning = function() {
                $scope.ui.addError("ERROR: The server responds abnormally. Please refresh the page or <a href='mailto:support@imnicy.com'>mail to me</a>.");
            };


            /**
             * This method adds information.
             *
             * @return {void}
             */
            $scope.ui.addInfo = function(s,d,x,pt) {
                var dc = (d?d:'green');

                if(s.indexOf(': ') !== -1) {
                    str = s.split(': ');
                    str[0] = $scope.ui.dye(str[0], dc);
                    str[1] = $scope.ui.dye(str[1], 'gray');
                    str = str.join(': ');
                    $scope.ui.addLine($scope.ui.dye((x?x:'🚥'), dc) + ' ' + str);
                } else {
                    str = s;
                    $scope.ui.addLine($scope.ui.dye((x?x:'🚥') + ' ' + str, dc));
                }

                if(pt) {
                    $scope.ui.addLine($scope.ui.halfBr());
                }
            };


            /**
             * This method adds text.
             *
             * @return {void}
             */
            $scope.ui.addText = function(s,d,x) {
                if(s.indexOf(': ') !== -1) {
                    str = s.split(': ');
                    str[0] = $scope.ui.dye(str[0], 'blue');
                    str[1] = $scope.ui.dye(str[1], 'white');
                    str = str.join(': ');
                    $scope.ui.addLine($scope.ui.dye('💬 ','white') + str,'blue');
                } else {
                    str = s;
                    $scope.ui.addLine($scope.ui.dye('💬 ' + str,'blue'));
                }
            };


            /**
             * This method adds error.
             *
             * @return {void}
             */
            $scope.ui.addError = function(s) {
                if(s.indexOf(': ') !== -1) {
                    str = s.split(': ');
                    str[0] = $scope.ui.dye(str[0], 'red');
                    str[1] = $scope.ui.dye(str[1], 'white');
                    str = str.join(': ');
                    $scope.ui.addLine($scope.ui.dye('📛 ','white') + str,'red');
                } else {
                    str = s;
                    $scope.ui.addLine($scope.ui.dye('📛 ' + str, 'red'));
                }
            };


            /**
             * This method adds warning.
             *
             * @return {void}
             */
            $scope.ui.addWarning = function(s, xc, pb) {
                if(xc) {
                    xcc = xc;
                } else {
                    xcc = 'yellow';
                }

                if(s.indexOf(': ') !== -1) {
                    str = s.split(': ');
                    str[0] = $scope.ui.dye(str[0], xcc);
                    str[1] = $scope.ui.dye(str[1], 'white');
                    str = str.join(': ');
                    $scope.ui.add($scope.ui.dye('🔶'+' ', 'white') + str);
                } else {
                    str = s;
                    $scope.ui.add($scope.ui.dye('🔶'+' '+str, xcc));
                }

                if(pb) {
                    $scope.ui.add($scope.ui.br());
                }
            };


            /**
             * This method adds title.
             *
             * @return {void}
             */
            $scope.ui.addTitle = function(s,d) {
                var dc = (d===true)?'orange':'green';
                $scope.ui.add([$scope.ui.dye($scope.ui.divider(), dc),$scope.ui.dye(s, dc),$scope.ui.dye($scope.ui.divider(), dc)]);
            };


            /**
             * This method get data from server
             *
             * @returns {$http}
             */
            $scope.http.api = function(data, config) {
                if($scope.term.preQuery) {
                    app = $scope.term.preQuery;
                    command = $scope.query.replace($scope.term.preQuery+' ','');
                } else {
                    qs = $scope.query.split(' ');
                    app = qs.shift();
                    command = qs.join('/');
                }

                if (command === "" || command === undefined) {
                    command = 'index';
                }

                return $scope.http._get('post', '/'+app+'/'+command, data, config);
            };


            /**
             * A common function to make request with csrf
             *
             * @returns {$http}
             */
            $scope.http.get = function(url, config) {
                return $scope.http._get('get', url, null, config);
            };


            /**
             * Run apps with query
             *
             * @param query
             * @returns {*|void}
             */
            $scope.http.run = function(query) {
                return $scope.http._get('post', '/run', {query: query});
            };


            $scope.http._get = function(type, url, data, config) {
                url = '/api/v1/apps' + url;

                var csrfToken = {'X-CSRF-TOKEN' : terminal_data.token};

                if (config === undefined) {
                    config = {headers : csrfToken};
                }
                else {
                    if (config.headers !== undefined) {
                        config.headers['X-CSRF-TOKEN'] = csrfToken['X-CSRF-TOKEN'];
                    }
                    else {
                        config.headers = csrfToken;
                    }
                }

                if (type === "get") {
                    return $http.get(url, config);
                }
                else {
                    return $http.post(url, data, config);
                }
            }
        }
    };
});
