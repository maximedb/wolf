var app = angular.module('wolf', [])

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
  var request = {
   method: 'GET',
   url: 'http://192.168.99.100/api/user_state',
   headers: {
     'Content-Type': 'application/json'
   },
   params: {'user_id': $scope.userid}
  }

  function update_state(){
    $http(request).then(function(data){
      console.log(data)
      $scope.started = data.data.started
      $scope.users = data.data.users
      $scope.usertype = data.data.user_type
      $scope.roundtype = data.data.round_type
    }, function(error){
      console.log(error)
    })
  }

  $scope.show_card = function(){
    alert('Vous etes un.... ' + $scope.usertype)
  }

  $interval(update_state, 1000)
})


app.controller('mainView', function($scope, $interval, $http){
  console.log('hello')
  $scope.users = []
  $scope.game_id = parseInt(localStorage.getItem('gameid'))
  var request = {
   method: 'GET',
   url: 'http://192.168.99.100/api/main_state',
   headers: {
     'Content-Type': 'application/json'
   },
   params: {'game_id': $scope.game_id}
  }

  function update_state(){
    $http(request).then(function(data){
      $scope.users = data.data.users
      console.log(data)
    }, function(error){
      console.log(error)
    })
  }
  $interval(update_state, 1000)
})
