<?php

namespace App\Http\Controllers;

use Illuminate\Http\Request;
use Illuminate\Support\Facades\Auth;
use App\Models\User;

class LoginController extends Controller
{
    public function __construct()
    {
        $this->middleware('guest')->except('signout');
    }

    // Menampilkan halaman login
    public function index()
    {
        return view('signin.main');
    }

    // Fungsi untuk otentikasi
    public function authenticate(Request $request)
    {
        $credentials = $request->validate([
        'username' => 'required',
        'password' => 'required',
        ]);

        $remember = $request->filled('remember');
        
        if (!Auth::attempt($credentials, $remember)) {
            return back()->with('error', 'You entered the wrong credentials.');
        }

        $request->session()->regenerate();
        return redirect()->intended('/dashboard');
    }

    // Fungsi untuk logout
    public function signout()
    {
        Auth::logout();
        request()->session()->invalidate();
        request()->session()->regenerateToken();
        return redirect('/signin');
    }
}
