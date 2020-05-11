/**
 * Define app variable.
 */
var app = $scope.apps.help;
app.header = function(pro,callback) {

    $scope.ui.add([
        $scope.ui.br,
        $scope.ui.dye($scope.ui.divider('#'), 'darkgray'),
        $scope.ui.br,
    ]);

    var h = [];
    if(!pro) {
        h.push($scope.ui.dye(' _  _ ___ _    ___   ___  ', 'gr-yellow-2 nobot'));
        h.push($scope.ui.dye('| || | __| |  | _ \\\\ |__ \\\\ ', 'gr-yellow-3 nobot'));
        h.push($scope.ui.dye('| __ | _|| |__|  _/   /_/ ', 'gr-yellow-4 nobot'));
        h.push($scope.ui.dye('|_||_|___|____|_|    (_)  ', 'gr-yellow-5 nobot'));
    } else {

        h.push($scope.ui.dye('~~~~~~~~~~~~ '+$scope.ui.dye('☀','gr-yellow-1')+' ~~~', 'gr-green-5 nobot'));
        h.push($scope.ui.dye('█░░█ █▀▀ █░░ █▀▀█ ▀█ ', 'gr-yellow-2 nobot'));
        h.push($scope.ui.dye('█▀▀█ █▀▀ █░░ █░░█ █▀', 'gr-yellow-3 nobot'));
        h.push($scope.ui.dye('▀░░▀ ▀▀▀ ▀▀▀ █▀▀▀ ▄░', 'gr-yellow-5 nobot'));

    }

    if(pro) {
        hmsg = 'All available commands are listed below:';
    } else {
        hmsg = 'Basic commands are listed below:';
    }
    h.push($scope.ui.br());
    h.push($scope.ui.dye(hmsg,'lightgray'));
    h.push($scope.ui.br());

    $scope.ui.add(h, false, callback);

};

app.list = function(pro,only_app) {

    var rpt = 50;

    $scope.http.get('', {cache: true}).then(function(response){

        app_found = false;

        var add = [];

        // May cause a dead cycle
        // $scope.term.preQuery = only_app;

        response.data.apps.forEach(function(v,i){

            if(only_app && only_app !== v.name) {
                return;
            }

            app_found = true;

            add.push($scope.ui.listHeader(v.name.toUpperCase() + ' APP:' + v.info));

            for(var i=0,l=v['commands'].length; i<l; i++) {

                nv = v['commands'][i];
                var pro_filter = true;

                if(nv.pro === true && !pro) {
                    pro_filter = false;
                }

                if(pro_filter) {
                    var param = '';
                    arguments = nv.arguments;
                    if (arguments.length !== 0) {
                        for (let ai in arguments) {
                            param += ' <i>{'+arguments[ai]+'}</i>';
                        }
                    }
                    var opt = (nv.options.length !== 0)? ' --['+nv.options.join('|')+']':'';
                    var example = (nv.example===undefined||nv.example===null)?'':'<i>'+nv.example+'</i>';
                    var nvname = (nv.name!=='index') ? ' ' + nv.name : '';
                    var cmd_tag = '<cmd>'+v.name + nvname + param + '</cmd>' + $scope.ui.dye(opt, 'tomato');
                    var cc = $(cmd_tag).text().length;
                    var dots = $scope.ui.dye($scope.helpers.repeater('.', rpt - cc ), 'darkgray');
                    add.push(cmd_tag + (dots) + nv.help + ' ' + $scope.ui.dye(example, 'darkgray'));
                    add.push($scope.ui.halfBr());
                    //add.push($scope.ui.dye($scope.ui.hr('.'),'darkgray'));

                }
            }

            add.push($scope.ui.br);

        });

        if (only_app && app_found === false) {
            $scope.ui.addWarning('WARNING: App '+only_app+' does not exist. For help, please use <cmd>help pro</cmd> command.');
        }

        $scope.ui.add(add, false, function(){

            /*if(!pro) {

                if (only_app) {
                    $scope.ui.addInfo('Woo: You can simply enter commands <cmd>help app '+only_app+' pro</cmd> to get more help info.', 'green', '☀', true);
                }
                else {
                    var cmdsamples = '(for example <cmd>cmd layout nature</cmd>, <cmd>help pro</cmd>, etc..)';
                    cmdsamples = $scope.ui.dye(cmdsamples, 'yellow');
                    $scope.ui.addWarning('GETTING STARTED: This is a command-line interface for web operations. You can simply enter commands '+cmdsamples+' to the text input at the footer and it will execute, easy right?','🍓','blue',true);

                    $scope.ui.add($scope.ui.br,false,function(){
                        $scope.ui.addInfo('You can type <cmd>help pro</cmd> to see all commands.','tomato','💾 ',true);
                    });
                }

            } else {
                $scope.ui.addInfo('It\'s for advanced users. Please type <cmd>help</cmd> for basic commands if you don\'t understand anything.','tomato','㊗ ',true);
            }*/

        });
    });
};