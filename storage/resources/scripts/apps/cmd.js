/**
 * Define app.
 */
var app = $scope.apps.cmd;

if (!app.news_list) {
    app.news_list = [];
}

if (!app.search_list) {
    app.search_list = [];
}

app.layouts = function (cb) {
    $scope.ui.addInfo('Loading layouts..');

    var json = window.localStorage['layouts'];

    if (json !== undefined) {
        var data = JSON.parse(json);

        if (cb) {
            return cb(data)
        }
        else {
            return app.parseLayouts(data);
        }
    }

    $scope.http.api().then(function (response) {

        var data = response.data;

        window.localStorage['layouts'] = JSON.stringify(data);

        if (cb) {
            return cb(data);
        } else {
            return app.parseLayouts(data);
        }

    });
};

app.parseLayouts = function (data) {
    var rt = [];

    rt.push($scope.ui.divider('-'));
    rt.push($scope.ui.dye('Available layouts are listed below', 'orange'));
    rt.push($scope.ui.br());

    rt.push($scope.ui.dye("default", 'white') + $scope.ui.dye($scope.helpers.repeater('.', 19), 'darkgray') + 'Usage: <cmd>cmd layout default</cmd>');
    rt.push($scope.ui.br());

    for (var i = 0, t = data.length; i < t; i++) {
        var lt = data[i];
        if (lt.credits.indexOf('http') > -1 && lt.credits.indexOf('://') > -1) {
            crd = '<a href="' + lt.credits + '" target="_blank">' + lt.credits + '</a>';
        } else {
            crd = '<cmd>search ' + lt.credits + '</cmd>';
        }
        lts = 26 - lt.name.length;
        rt.push($scope.ui.dye(lt.name, 'white') + $scope.ui.dye($scope.helpers.repeater('.', lts), 'darkgray') + 'Usage: <cmd>cmd layout ' + lt.name + '</cmd>, Credits: ' + crd);
        rt.push($scope.ui.br());
    }

    $scope.ui.add(rt);
};

app.setLayout = function (name) {

    if (name == 'none' || name == 'black' || name == 'reset' || name == 'default' || name == 'layout' || name == 'null' || name == 'nil' || name == 'empty' || name == 'unset') {
        var lls = JSON.parse(window.localStorage['layout_data']);
        delete window.localStorage['layout_data'];
        $scope.ui.addWarning('Layout unset: ' + lls.name);
        return $scope.ui.runLayout();
    } else {
        var data = JSON.parse(window.localStorage['layouts']);

        for (var i = 0, t = data.length; i < t; i++) {
            if (data[i]['name'] == name) {
                window.localStorage['layout_data'] = JSON.stringify(data[i]);
                $scope.ui.addInfo('Layout loading: ' + name);
                return $scope.ui.runLayout();
                break;
            }
        }

        return $scope.ui.addError('No layouts found with name: ' + name);
    }
};

app.layout = function (name) {
    $scope.ui.addInfo('Searching layout: ' + name);

    if (!window.localStorage['layouts']) {
        app.layouts(function (data) {
            app.setLayout(name);
        });
    } else {
        app.setLayout(name);
    }
};

app.about = function () {
    var arr = [];
    arr.push($scope.ui.dye('              __ __    ___  _      _       ___             .  ', 'white'));
    arr.push($scope.ui.dye('   *         |  |  |  /  _]| |    | |     /   \\    o          ', 'white'));
    arr.push($scope.ui.dye('             |  |  | /  [_ | |    | |    |     |              ', 'white'));
    arr.push($scope.ui.dye('             |  _  ||    _]| |___ | |___ |  O  |     .        ', 'white'));
    arr.push($scope.ui.dye('        .    |  |  ||   [_ |     ||     ||     |              ', 'white'));
    arr.push($scope.ui.dye('             |  |  ||     ||     ||     ||     |         *    ', 'white'));
    arr.push($scope.ui.dye('             |__|__||_____||_____||_____| \\___/               ', 'white'));
    arr.push($scope.ui.dye('                                                                      .    ', 'white'));
    arr.push($scope.ui.dye('   .      o   WELCOME TO THE IMNICY.COM! CMD IS          o      ', 'white'));
    arr.push($scope.ui.dye('                 AN ONLINE COMMAND INTERFACE    .            ', 'white'));
    arr.push($scope.ui.dye('                     FOR WORLD WIDE WEB!           .          ', 'white'));
    arr.push($scope.ui.dye('            *                  .                          .    ', 'white'));
    arr.push($scope.ui.dye(' o                                         .                   ', 'white'));
    arr.push($scope.ui.dye('        .  YOU CAN LISTEN MUSIC, CREATE PLAYLISTS,   .             ', 'white'));
    arr.push($scope.ui.dye('              BROWSE PRODUCTHUNT & HACKER NEWS,              *   ', 'white'));
    arr.push($scope.ui.dye('     .         PLAY GAMES, BROWSE ASCII STUFF,        .             ', 'white'));
    arr.push($scope.ui.dye('                  SEARCH AT GOOGLE & MORE!               o', 'white'));
    arr.push($scope.ui.dye('         .                           *         .    ', 'white'));
    arr.push($scope.ui.dye(' .              IT\'S LIKE CHUCK NORRIS OF THE     ', 'white'));
    arr.push($scope.ui.dye('            INTERNET. PLATFORM IS DEVELOPED WITH              . ', 'white'));
    arr.push($scope.ui.dye('               JAVASCRIPT AND SOON DEVELOPERS   .', 'white'));
    arr.push($scope.ui.dye('      .      WILL BE ABLE TO PUBLISH THEIR OWN         .', 'white'));
    arr.push($scope.ui.dye('                 COMMANDS TO THE PLATFORM.     ', 'white'));
    arr.push($scope.ui.dye('      o                  .        *                      .     ', 'white'));
    arr.push($scope.ui.dye('   *              .                   o               .     ', 'white'));
    arr.push($scope.ui.dye('          DEVELOPED BY EMIR ALP (<a href="http://twitter.com/nerdsarewinning" target="_blank">@nerdsarewinning</a>)          ', 'white'));
    arr.push($scope.ui.dye('            CHECKOUT <a href="http://emiralp.com" target="_blank">emiralp.com</a> FOR MORE INFO            ', 'white'));
    arr.push($scope.ui.dye('           *                                   .            .    ', 'white'));

    $scope.ui.add(arr);
};

app.search = function(query) {

    $scope.ui.addInfo('Searching: ' + query);

    $scope.http.api({query: encodeURIComponent(query)}).then(function (response) {

        if (response.status !== 200) {
            $scope.ui.addError('Something went wrong, please try again.');
            return ;
        }

        var data = response.data;

        $scope.ui.addWarning('Sorry! This function is not open.');
    });
};

app.go = function(url) {

    if (url.indexOf('http') === -1) {
        url = 'http://' + url;
    }

    $scope.ui.windowOpen(url);
};

/**
 * Run app
 */
app.init = function () {

    if (app.inited !== true) {

    }

    app.inited = true;

};

app.init();