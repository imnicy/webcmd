/**
 * Define app.
 */
var app = $scope.apps.user;

app._validateSignup = function () {

    errors_arr = [];

    if (
        !$scope.tempUserData.fullname ||
        !$scope.tempUserData.email ||
        !$scope.tempUserData.password ||
        !$scope.tempUserData.password_confirmation ||
        !$scope.tempUserData.username
    ) {
        errors_arr.push('All fields are required');
        return errors_arr;
    }

    if ($scope.tempUserData.password !== $scope.tempUserData.password_confirmation) {
        errors_arr.push('Passwords doesn\'t match');
    } else if ($scope.tempUserData.password.length < 6) {
        errors_arr.push('Password is too short');
    }

    if ($scope.tempUserData.email.indexOf('@') === -1 || $scope.tempUserData.email.indexOf('.') === -1) {
        errors_arr.push('Email is wrong');
    }

    if ($scope.tempUserData.username.length < 3) {
        errors_arr.push('Username is too short');
    }

    return errors_arr;
};

app._validateUpdate = function () {

    errors_arr = [];

    if (
        !$scope.tempUserData.fullname ||
        !$scope.tempUserData.email ||
        !$scope.tempUserData.username
    ) {
        errors_arr.push('All fields are required');
        return errors_arr;
    }

    if ($scope.tempUserData.password !== undefined && $scope.tempUserData.password !== $scope.tempUserData.password_confirmation) {
        errors_arr.push('Passwords doesn\'t match');
    } else if ($scope.tempUserData.password !== undefined && $scope.tempUserData.password.length < 6) {
        errors_arr.push('Password is too short');
    }

    if ($scope.tempUserData.email.indexOf('@') === -1 || $scope.tempUserData.email.indexOf('.') === -1) {
        errors_arr.push('Email is wrong');
    }

    if ($scope.tempUserData.username.length < 3) {
        errors_arr.push('Username is too short');
    }

    $scope.http.api();

    return errors_arr;
};


app.signin = function () {

    if (localStorageService.get('access_token')) {
        return $scope.ui.addError('You are already logged in. You can logout by using <cmd>user logout</cmd> cmd.');
    }

    $scope.ui.add([$scope.ui.br(), $scope.ui.listHeader('🔒LOGIN'), $scope.ui.br()], function () {
        var username_or_email = '';
        var password = '';

        $scope.ui.prompt('Username or email', false, false, function (resp) {
            username_or_email = resp;
            $scope.ui.addWarning('Entered username or email: ' + resp);
            $scope.ui.prompt('Password', true, false, function (resp) {
                password = resp;
                $scope.ui.addWarning('Entered password: ' + $scope.helpers.repeater('*', (resp ? resp.length : 8)));
                $scope.ui.addInfo('Setting up XMLHttpRequest..');

                $timeout(function () {
                    $scope.ui.addInfo('Please wait... Authenticating new session...');

                    $timeout(function () {
                        $scope.http.api({email_or_username: username_or_email, password: password}).success(function (data, status, headers) {
                            if (data.status) {
                                $scope.ui.addWarning('You are now logged in..', '🌟');
                                var _token = headers('Authorization');
                                if (_token !== null) {
                                    localStorageService.add('access_token', _token);
                                }
                            } else if (data.error_text !== undefined) {
                                $scope.ui.addError(data.error_text);
                            } else {
                                $scope.ui.addError('Something went wrong. Please try again later.');
                            }
                        });
                    }, 400);
                }, 400);
            });
        });
    });
};

app.resend = function (email) {

    $scope.ui.add([$scope.ui.br(), $scope.ui.listHeader('📩RESEND CONFIRMATION'), $scope.ui.br()], undefined, function () {
        if (email === undefined || email === 'resend') {
            email = '';
            $scope.ui.prompt('Email address', false, false, function (resp) {
                email = resp;
                $scope.ui.addWarning('Entered email address: ' + resp);
                $scope.ui.addInfo('Setting up XMLHttpRequest..');

                $timeout(function () {
                    $scope.ui.addInfo('Please wait... Sending request to imnicy.com servers...');

                    $scope.http.api({email: email}).success(function (data) {
                        if (data.status) {
                            $scope.ui.addInfo('Your confirmation token has been resent.');
                        } else if (data.error_text !== undefined) {
                            $scope.ui.addError(data.error_text);
                        } else {
                            $scope.ui.addError('Something went wrong. Maybe account is already activated.');
                        }
                    });
                }, 400);
            });
        } else {
            $scope.ui.addInfo('Setting up XMLHttpRequest..');

            $timeout(function () {
                $scope.ui.addInfo('Please wait... Sending request to imnicy.com servers...');

                $scope.http.api({email: email}).success(function (data) {
                    if (data.status) {
                        $scope.ui.addInfo('Your confirmation token has been resent.');
                    } else if (data.error_text !== undefined) {
                        $scope.ui.addError(data.error_text);
                    } else {
                        $scope.ui.addError('Something went wrong. Maybe account is already activated.');
                    }
                });
            }, 400);
        }
    });
};

app.show = function (username) {

    var show_profile = function(username) {
        $scope.ui.addInfo('Setting up XMLHttpRequest..');

        $timeout(function () {
            $scope.ui.addInfo('Please wait... Sending request to imnicy.com servers...');

            $scope.http.api({username: username}).success(function (data) {
                if (data.status) {
                    $scope.ui.add([$scope.ui.br(), $scope.ui.listHeader('👤PROFILE:' + username || ''), $scope.ui.br()], function () {
                        angular.forEach(data.user_data, function (value, key) {
                            if (value) {
                                $scope.ui.addInfo(key.toUpperCase().replace('_', ' ') + ': ' + value, undefined, '<span style=\'color:white\'>-></span>');
                            }
                        });

                        $scope.ui.addLine($scope.ui.br());
                        $scope.ui.addWarning('Done: Parse user profile');
                    });
                } else if (data.error_text !== undefined) {
                    $scope.ui.addError(data.error_text);
                } else {
                    $scope.ui.addError('Something went wrong.');
                }
            });
        }, 400);
    };

    if (username === undefined || username === "") {
        username = '';
        $scope.ui.prompt('Enter an username to show profile (type \'me\' for your profile)', false, false, function (resp) {
            username = resp;
            $scope.ui.addWarning('Username: ' + resp);
            show_profile(username)
        });
    }
    else {
        show_profile(username)
    }
};

app.recover = function (email_or_username) {
    $scope.ui.add([$scope.ui.br(), $scope.ui.listHeader('📩RECOVER ACCOUNT'), $scope.ui.br()], function () {

        if (email_or_username === undefined || email_or_username === 'retrieve' || email_or_username === 'recover' || email_or_username === 'forget') {
            $scope.ui.prompt('Email or username', false, false, function (resp) {
                email_or_username = resp;
                $scope.ui.addWarning('Entered email or username: ' + resp);
                $scope.ui.addInfo('Setting up XMLHttpRequest..');

                $timeout(function () {
                    $scope.ui.addInfo('Please wait... Sending request to imnicy.com servers...');

                    $scope.http.api({email_or_username: email_or_username}).success(function (data) {
                        if (data.status) {
                            $scope.ui.addInfo('Email has been sent to your email.');
                        } else if (data.error_text !== undefined) {
                            $scope.ui.addError(data.error_text);
                        } else {
                            $scope.ui.addError('Something went wrong. Maybe account is already activated.');
                        }
                    });
                }, 400);
            });
        } else {
            $scope.ui.addInfo('Setting up XMLHttpRequest..');

            $timeout(function () {
                $scope.ui.addInfo('Please wait... Sending request to imnicy.com servers...');

                $scope.http.api({email_or_username: email_or_username}).success(function (data) {
                    if (data.status) {
                        $scope.ui.addInfo('Email has been sent to your email.');
                    } else if (data.error_text !== undefined) {
                        $scope.ui.addError(data.error_text);
                    } else {
                        $scope.ui.addError('Something went wrong. Maybe account is already activated.');
                    }
                });
            }, 400);
        }
    });
};

app.signup = function () {
    $scope.ui.add([$scope.ui.br(), $scope.ui.listHeader('🔓SIGNUP'), $scope.ui.br()], function () {
        if (!$scope.tempUserData) {
            $scope.tempUserData = {};
        }

        $scope.ui.prompt('Email', false, $scope.tempUserData.email, function (resp) {
            $scope.tempUserData.email = resp;
            $scope.ui.addWarning('Entered email address: ' + resp);
            $scope.ui.prompt('Username (min 3 chars)', false, $scope.tempUserData.username, function (resp) {

                $scope.tempUserData.username = resp;
                $scope.ui.addWarning('Entered username: ' + resp);

                $scope.ui.prompt('Full name', false, $scope.tempUserData.fullname, function (resp) {

                    $scope.tempUserData.fullname = resp;
                    $scope.ui.addWarning('Entered name: ' + resp);

                    $scope.ui.prompt('Password (min 6 chars)', true, false, function (resp) {

                        $scope.tempUserData.password = resp;
                        $scope.ui.addWarning('Entered password: ' + $scope.helpers.repeater('*', (resp ? resp.length : 8)));

                        $scope.ui.prompt('Password again (repeat)', true, false, function (resp) {

                            $scope.tempUserData.password_confirmation = resp;
                            $scope.ui.addWarning('Entered password confirmation: ' + $scope.helpers.repeater('*', (resp ? resp.length : 8)));

                            // --
                            $scope.ui.addInfo('Running client-side validations, please wait..');
                            has_signup_errors = app._validateSignup();

                            if (has_signup_errors.length > 0) {
                                $scope.ui.addError('We have problems: ' + has_signup_errors.join(' & '));
                                return false;
                            }

                            $scope.ui.addInfo('Setting up XMLHttpRequest..');

                            $timeout(function () {
                                $scope.ui.addInfo('Running server-side validations, please wait..');

                                $timeout(function () {

                                    var p = $scope.tempUserData;

                                    data_to_send = {
                                        'email': p.email,
                                        'password': p.password,
                                        'password_confirmation': p.password_confirmation,
                                        'username': p.username,
                                        'fullname': p.fullname
                                    };

                                    $scope.http.api(data_to_send).success(function (data) {
                                        if (data.status) {
                                            //app.welcome();
                                        } else if (data.error_text !== undefined) {
                                            $scope.ui.add($scope.ui.divider('*'), function () {
                                                $scope.ui.addError('We have problems: ' + data.error_text);
                                            });
                                        } else {
                                            $scope.ui.add($scope.ui.divider('*'), function () {
                                                $scope.ui.addError('Authentication failed, please check your email/username and password.');
                                                $scope.ui.addWarning('If you forget your username/email or password, please use <cmd>user recover</cmd> command.');
                                            });
                                        }
                                    });
                                }, 400);
                            }, 400);
                        });
                    });
                });
            });
        });
    });
};

app._update = function () {

    // --
    $scope.ui.addInfo('Running client-side validations, please wait..');
    has_signup_errors = app._validateUpdate();

    if (has_signup_errors.length > 0) {
        $scope.ui.addError('We have problems: ' + has_signup_errors.join(' & '));
        return false;
    }

    $scope.ui.addInfo('Setting up XMLHttpRequest..');

    $timeout(function () {
        $scope.ui.addInfo('Running server-side validations, please wait..');
        $timeout(function () {

            var p = $scope.tempUserData;
            data_to_send = {};

            if (p.email) {
                data_to_send.email = p.email;
            }

            if (p.username) {
                data_to_send.username = p.username;
            }

            if (p.fullname) {
                data_to_send.fullname = p.fullname;
            }

            if (p.password && p.password_confirmation) {
                data_to_send.password = p.password;
                data_to_send.password_confirmation = p.password_confirmation;
            }

            if (p.gender) {
                if ($.trim(p.gender.toLowerCase()) === 'm' || $.trim(p.gender.toLowerCase()) === 'male' || $.trim(p.gender.toLowerCase()) === 'he') {
                    data_to_send.gender = 'm';
                } else if ($.trim(p.gender.toLowerCase()) === 'f' || $.trim(p.gender.toLowerCase()) === 'female' || $.trim(p.gender.toLowerCase()) === 'she') {
                    data_to_send.gender = 'f';
                } else {
                    data_to_send.gender = '?';
                }
            }

            if (p.webpage) {
                if (p.webpage.indexOf('http') === -1) {
                    data_to_send.webpage = 'http://' + p.webpage;
                } else {
                    data_to_send.webpage = p.webpage;
                }
            }

            if (p.bio) {
                data_to_send.bio = p.bio;
            }

            if (p.avatar) {
                data_to_send.avatar = p.avatar;
            }

            if (p.tags) {
                data_to_send.tags = p.tags;
            }

            if (p.twitter_username) {
                data_to_send.twitter_username = p.twitter_username;
            }

            if (p.facebook_username) {
                data_to_send.facebook_username = p.facebook_username;
            }

            if (p.github_username) {
                data_to_send.github_username = p.github_username;
            }

            $scope.http.api(data_to_send).success(function (data) {
                if (data.status) {
                    $scope.ui.addWarning('Your profile has been updated!');

                } else if (data.error_text !== undefined) {
                    $scope.ui.add($scope.ui.divider('*'), function () {
                        $scope.ui.addError('We have problems: ' + data.error_text);
                    });
                } else {
                    $scope.ui.addError('Something went wrong. Please try again.');
                }
            });
        }, 400);
    }, 400);
};

app._zeroPad = function (num, places) {
    var zero = places - num.toString().length + 1;
    return Array(+(zero > 0 && zero)).join('0') + num;
};

app._ask_more_details = function () {
    $scope.ui.ask('Do you want to update your public profile?', true, function (resp) {
        if (resp) {
            $scope.http.api().success(function (avatars) {
                $scope.ui.prompt('Your emoji avatar (use up/down keys)', false, [$scope.tempUserData.avatar, avatars], function (resp) {

                    $scope.tempUserData.avatar = resp;
                    $scope.ui.addWarning('Your avatar: ' + resp);

                    $scope.ui.prompt('Gender (m/f/*)', false, $scope.tempUserData.gender, function (resp) {

                        $scope.tempUserData.gender = resp;
                        $scope.ui.addWarning('Your gender: ' + resp);

                        $scope.ui.prompt('Webpage', false, $scope.tempUserData.webpage, function (resp) {

                            $scope.tempUserData.webpage = resp;
                            $scope.ui.addWarning('Your webpage: ' + resp);

                            $scope.ui.prompt('Github username', false, $scope.tempUserData.github_username, function (resp) {
                                $scope.tempUserData.github_username = resp;
                                $scope.ui.addWarning('Your Github username: ' + resp);

                                $scope.ui.prompt('Want to tag yourself (Ex: developer, nodejs, nerd, big data, ..)', false, $scope.tempUserData.tags, function (resp) {
                                    $scope.tempUserData.tags = resp;
                                    $scope.ui.addWarning('Tags: ' + resp);

                                    app._ask_password_change();
                                });
                            });
                        });
                    });
                });
            });
        } else {
            app._ask_password_change();
        }
    });
};

app._ask_password_change = function () {
    $scope.ui.ask('Do you want to change your password?', false, function (resp) {
        if (resp) {
            $scope.ui.prompt('Pssword (min 6 chars)', true, false, function (resp) {

                $scope.tempUserData.password = resp;
                $scope.ui.addWarning('Entered password: ' + $scope.helpers.repeater('*', (resp ? resp.length : 8)));

                $scope.ui.prompt('Password again (repeat)', true, false, function (resp) {
                    $scope.tempUserData.password_confirmation = resp;
                    $scope.ui.addWarning('Entered password confirmation: ' + $scope.helpers.repeater('*', (resp ? resp.length : 8)));
                    app._update();
                });

            });
        } else {
            app._update();
        }
    });
};

app.update = function () {
    if (!localStorageService.get('access_token')) {
        return $scope.ui.addLogin();
    }

    $scope.ui.add([$scope.ui.br(), $scope.ui.listHeader('📝UPDATE'), $scope.ui.br()], function () {

        $scope.http.api({}, undefined, 'user', 'show me').then(function (response_data) {
            data = response_data.data;

            if (data.status === true) {

                $scope.tempUserData = data.user_data;
                $scope.ui.prompt('Full name', false, $scope.tempUserData.fullname, function (resp) {
                    $scope.tempUserData.fullname = resp;
                    $scope.ui.addWarning('Entered name: ' + resp);

                    app._ask_more_details();
                });
            } else {
                return $scope.ui.addError('User not found.');
            }
        });
    });
};

app.signout = function () {
    $scope.http.api().success(function (data) {
        if (data.status) {
            localStorageService.remove('access_token');
            $scope.ui.addWarning('You are now logged out..');
        }
    });
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