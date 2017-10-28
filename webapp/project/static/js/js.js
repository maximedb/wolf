var app = angular.module('wolf', [])

app.controller('mainView', function($scope, $http){
  var req = {
   method: 'POST',
   url: 'http://192.168.99.100/api/user',
   headers: {
     'Content-Type': 'application/json'
   },
   data: {'username': 'username'}
  }
  $http(req).then(function(data){
    $scope.userid = data.data.userid;
    $scope.username = data.data.username;
    return $http
  }, function(error){
    alert(error.statusText)
  }).then(function(data))
  console.log('hello')
})
