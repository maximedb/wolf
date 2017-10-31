var app = angular.module('wolf', [])

Array.prototype.diff = function(a) {
  return this.filter(function(i) {return a.map(function(e) { return JSON.stringify(e); }).indexOf(JSON.stringify(i)) < 0;});
};

function getDiff(past, now) {
  let ret = { add: [], remove: [] };
  for (var i = 0; i < now.length; i++) {
    if (past.indexOf(now[i]) < 0)
      ret['add'].push(now[i]);
  }
  for (var i = 0; i < past.length; i++) {
    if (now.indexOf(past[i]) < 0)
      ret['remove'].push(past[i]);
  }
  return ret;
}

app.controller('startView', function($scope, $http, $window){
  var request = {
   method: 'POST',
   url: 'http://192.168.99.100/api/user',
   headers: {
     'Content-Type': 'application/json'
   },
   data: {'username': 'username'}
  }

  $scope.create_village = function(){
    request.url = 'http://192.168.99.100/api/game';
    request.data = {'game_name': 'mes_couilles_dans_ta'}
    $http(request).then(function(data){
      console.log(data);
      $scope.game_id = data.data.game_id
      localStorage.setItem('gameid', $scope.game_id)
      $window.location.href = 'main.html';
    })
  }

  $scope.join_game = function(){
    request.url =  'http://192.168.99.100/api/user'
    var data = {'username': $scope.user_name}
    request.data = data
    $http(request).then(function(data){
      $scope.userid = data.data.userid;
      localStorage.setItem('userid', data.data.userid)
      localStorage.setItem('gameid', $scope.game_id)
      $scope.username = data.data.username;
      request.url = 'http://192.168.99.100/api/join'
      request.data = {
        'user_id': $scope.userid,
        'game_id': $scope.game_id
      }
      return $http(request)
    }).then(function(data){
      // Ok let's go the gaaaame
      console.log(data)
    }, function(error){
      console.log(error)
    })
  }

  console.log('hello')
})

app.controller('playerView', function($scope, $http, $interval){
  console.log('hello')
  $scope.users = []
  $scope.started = false
  $scope.userid = parseInt(localStorage.getItem('userid'))
  $scope.gameid = parseInt(localStorage.getItem('gameid'))
  $scope.voted_for = undefined;

  var request = {
   method: 'GET',
   url: 'http://192.168.99.100/api/user_state',
   headers: {
     'Content-Type': 'application/json'
   },
   params: {'user_id': $scope.userid}
  }

  function update_state(){
    request.url = 'http://192.168.99.100/api/user_state'
    request.method = 'GET'
    request.params = {'user_id': $scope.userid}
    $http(request).then(function(data){
      console.log(data)
      $scope.started = data.data.started
      $scope.users = data.data.users
      $scope.usertype = data.data.user_type
      $scope.roundtype = data.data.round_type
      $scope.voted_for = data.data.voted_for
    }, function(error){
      console.log(error)
    })
  }

  $scope.show_card = function(){
    console.log($scope.usertype)
    alert('Vous etes un.... ' + $scope.usertype)
  }

  $scope.vote_for = function(user_to, event, alive){
    if (!alive) return
    console.log('hey')
    request.method = 'POST'
    request.url = 'http://192.168.99.100/api/vote'
    request.data = {'user_from_id': $scope.userid,
                    'user_to_id': user_to,
                    'game_id': $scope.gameid}
    console.log('helloe')
    $http(request).then(function(data){
      $scope.voted_for = user_to
      console.log(data)
    }, function(error){
      console.log(error)
    })
    event.preventDefault()
  }

  $interval(update_state, 1000)
})


app.controller('mainView', function($scope, $interval, $http, $timeout){
  console.log('hello')
  $scope.started = false
  $scope.users = []
  $scope.game_id = parseInt(localStorage.getItem('gameid'))
  $scope.userid = parseInt(localStorage.getItem('userid'))
  $scope.time_until_end = undefined;
  $scope.round_type = undefined;
  $scope.current_round = undefined;
  $scope.show_result = false;
  $scope.byebye = '';
  $scope.logs = []

  var request = {
   method: 'GET',
   url: 'http://192.168.99.100/api/main_state',
   headers: {
     'Content-Type': 'application/json'
   },
   params: {'game_id': $scope.game_id}
  }

  function update_state(){
    request.method = 'GET'
    request.url = 'http://192.168.99.100/api/main_state'
    request.params = {'game_id': $scope.game_id}
    $http(request).then(function(data){
      $scope.started = data.data.status
      $scope.time_until_end = Date.parse(data.data.end_time)
      if ((data.data.round_id != $scope.current_round) & ($scope.current_round != undefined) ){
        show_the_results(data.data.users)
      }
      $scope.round_type = data.data.round_type
      $scope.current_round = data.data.round_id
      $scope.users = data.data.users
      console.log(data)
    }, function(error){
      console.log(error)
    })
  }

  function show_the_results(users){
    for (var i = 0; i < users.length; i++) {
      if ($scope.users[i].status != users[i].status){
        console.log('deadman', users[i])
        $scope.byebye = users[i].user_name
        $scope.show_result = true
        $timeout(function(){$scope.show_result = false}, 60000)
      }
    }
  }

  $scope.start_game = function(){
    request.method = 'POST'
    request.url = 'http://192.168.99.100/api/start_game'
    request.data = {'game_id': $scope.game_id}
    $http(request).then(function(data){
      console.log(data)
    }, function(error){
      console.log(error)
    })
  }

  $scope.kill_user = function(user_id){
    request.method = 'POST'
    request.url = 'http://192.168.99.100/api/kill'
    request.data = {'user_id': user_id}
    $http(request).then(function(data){
      console.log(data)
    }, function(error){
      console.log(error)
    })
  }

  function udpate_timer(){
    var now = new Date().getTime();
    var distance = $scope.time_until_end - now;
    var minutes = 60 + Math.floor((distance % (1000 * 60 * 60)) / (1000 * 60));
    var seconds = 60 + Math.floor((distance % (1000 * 60)) / 1000);
    minutes = (minutes < 0) ? 0 : minutes
    seconds = (seconds < 0) ? 0 : seconds
    $scope.minutes = (minutes < 10) ? '0' + minutes : ''+minutes
    $scope.seconds = (seconds < 10) ? '0' + seconds : ''+seconds
  }

  $interval(update_state, 1000)
  $interval(udpate_timer, 1000)
})

app.filter('numberFixedLen', function () {
    return function(a,b){
        return(1e4+""+a).slice(-b);
    };
});
