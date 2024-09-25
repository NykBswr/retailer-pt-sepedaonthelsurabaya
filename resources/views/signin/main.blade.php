@extends('layout.main')

@section('container')
    <section class="flex h-screen w-screen items-center justify-center" id="signIn">
        <div class="flex h-full w-full flex-col items-center justify-between">
            <div class="mt-5 flex h-full w-full items-center justify-center">
                <img class="h-[7vh] w-auto" src={{ asset('img/LogoWhite.svg') }} alt="Logo">
            </div>
            <form action="{{ route('signin') }}" method="post"
                class="flex h-auto w-[65vw] flex-col items-center justify-center sm:w-[50vw] md:w-[35vw] lg:w-[28vw]">
                @csrf
                <h1
                    class='mb-10 bg-gradient-to-tl from-secondary to-primary bg-clip-text text-center text-xl font-extrabold text-transparent sm:text-2xl md:text-3xl lg:text-4xl'>
                    Welcome back</h1>
                <div class="mb-3 w-full cursor-pointer rounded-md bg-gradient-to-tl from-secondary to-primary p-[2px]">
                    <input
                        class="flex w-full items-center justify-between rounded-md border-0 bg-white px-3 py-2 text-xs font-medium text-dark outline-0 outline-transparent ring-0 ring-transparent placeholder:text-primary focus:border-0 focus:ring-secondary md:text-sm lg:text-base"
                        type="text" name="username" placeholder="Username*" autofocus required>
                </div>
                <div class="mb-3 w-full cursor-pointer rounded-md bg-gradient-to-tl from-secondary to-primary p-[2px]">
                    <input
                        class="flex w-full items-center justify-between rounded-md border-0 bg-white px-3 py-2 text-xs font-medium text-dark outline-0 outline-transparent ring-0 ring-transparent placeholder:text-primary focus:border-0 focus:ring-secondary md:text-sm lg:text-base"
                        type="password" name="password" placeholder="Passwords*" required>
                </div>
                <button type="submit" class='w-full rounded-md font-semibold text-white hover:opacity-80'>
                    <h1 class="h-full w-full rounded-md bg-gradient-to-tl from-secondary to-primary px-3 py-2">Sign In</h1>
                </button>
            </form>
            <div class='mb-5 flex h-full flex-col justify-end'>
                <h1 class='text-xs text-primary lg:text-sm'>
                    <a href="">Terms of Use</a> | <a href="">Privacy Policy</a>
                </h1>
            </div>
        </div>
    </section>
@endsection
