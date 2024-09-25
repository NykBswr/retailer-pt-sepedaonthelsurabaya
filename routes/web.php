<?php

use App\Models\User;
use Illuminate\Support\Facades\Route;
use App\Http\Controllers\UserController;
use App\Http\Controllers\LoginController;
use App\Http\Controllers\DashboardController;

/*
|--------------------------------------------------------------------------
| Web Routes
|--------------------------------------------------------------------------
|
| Here is where you can register web routes for your application. These
| routes are loaded by the RouteServiceProvider and all of them will
| be assigned to the "web" middleware group. Make something great!
|
*/

// Profle Kelompok
Route::get('/', function () {
return view('profile-kelompok.main');
});
Route::get('/profileKelompok', function () {
return view('profile-kelompok.main');
});

// LOGIN
Route::get('/signin', [LoginController::class, 'index'])->name('signin')->middleware('guest');
Route::post('/signin', [LoginController::class, 'authenticate']);
Route::post('/signout', [LoginController::class, 'signout'])->name('signout');

// DASHBOARD
Route::get('/dashboard', [DashboardController::class, 'index'])->middleware('auth');
