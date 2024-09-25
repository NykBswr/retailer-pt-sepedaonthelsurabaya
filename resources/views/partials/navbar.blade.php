<nav class="fixed w-full border-dark bg-white px-12 py-5 shadow-md">
    <div class="flex items-center justify-between">
        <a href="#" class="flex items-center space-x-3 rtl:space-x-reverse">
            <img src="{{ asset('img/LogoWhite.svg') }}" class="h-[5vh] w-auto" alt="Group Logo" />
        </a>
        <button data-collapse-toggle="navbar-default" type="button"
            class="hover:bg-primay inline-flex h-10 w-10 items-center justify-center rounded-lg p-2 text-sm text-dark focus:outline-none md:hidden"
            aria-controls="navbar-default" aria-expanded="false">
            <span class="sr-only">Open main menu</span>
            <svg class="h-5 w-5" aria-hidden="true" xmlns="http://www.w3.org/2000/svg" fill="none"
                viewBox="0 0 17 14">
                <path stroke="currentColor" stroke-linecap="round" stroke-linejoin="round" stroke-width="2"
                    d="M1 1h15M1 7h15M1 13h15" />
            </svg>
        </button>
        <div class="hidden w-full md:block md:w-auto" id="navbar-default">
            @if (auth()->check())
                <ul
                    class="md border-primay mt-4 flex flex-col rounded-lg border bg-gray-50 p-4 font-medium rtl:space-x-reverse md:mt-0 md:flex-row md:space-x-8 md:border-0 md:bg-white md:p-0">
                    <li class="flex items-center">
                        <a href="#" class="mr-3 block rounded text-base text-dark md:p-0" aria-current="page">
                            Welcome, {{ auth()->user()->username }}</a>
                        <button id="dropdownUserAvatarButton" data-dropdown-toggle="dropdownAvatar"
                            class="rounded-full bg-gradient-to-tl from-secondary to-primary p-[0.15rem]" type="button">
                            <img class="h-[5vh] w-auto" src="{{ asset('img/logo.png') }}" alt="Profile Profile">
                        </button>
                    </li>
                </ul>
            @else
                <a href="/signin"
                    class="h-full w-full rounded-md bg-gradient-to-tl from-secondary to-primary px-3 py-2 font-semibold text-white hover:opacity-80">
                    Sign In
                </a>
            @endif
            <div id="dropdownAvatar" class="z-10 hidden w-[13vw]">
                <div class="mr-5 items-center justify-center rounded-md bg-white shadow-md">
                    {{-- <ul class="px-2 py-1" aria-labelledby="dropdownUserAvatarButton">
                        <li
                            class="flex flex-row items-center rounded-md from-secondary to-primary px-2 text-sm text-dark hover:bg-gradient-to-tl hover:text-white">
                            <svg class="h-[1.8vw] w-[1.8vw]" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"
                                width="24" height="24" fill="none" viewBox="0 0 24 24">
                                <path stroke="currentColor" strokeLinecap="square" strokeLinejoin="round"
                                    strokeWidth="2"
                                    d="M10 19H5a1 1 0 0 1-1-1v-1a3 3 0 0 1 3-3h2m10 1a3 3 0 0 1-3 3m3-3a3 3 0 0 0-3-3m3 3h1m-4 3a3 3 0 0 1-3-3m3 3v1m-3-4a3 3 0 0 1 3-3m-3 3h-1m4-3v-1m-2.121 1.879-.707-.707m5.656 5.656-.707-.707m-4.242 0-.707.707m5.656-5.656-.707.707M12 8a3 3 0 1 1-6 0 3 3 0 0 1 6 0Z" />
                            </svg>
                            <a href="#" class="ml-2 block py-2">Settings</a>
                        </li>
                    </ul> --}}
                    {{-- <div class="mx-2 mt-1 rounded-md border-b border-primary"></div> --}}
                    <div class="px-2 py-2">
                        <form action="/signout" method="post"
                            class="rounded-md px-2 text-sm text-dark hover:bg-gradient-to-tl hover:from-secondary hover:to-primary hover:text-white">
                            @csrf
                            <button type="submit" class="flex flex-row items-center justify-center">
                                <svg class="h-[1.8vw] w-[1.8vw]" aria-hidden="true" xmlns="http://www.w3.org/2000/svg"
                                    width="24" height="24" fill="none" viewBox="0 0 24 24">
                                    <path stroke="currentColor" strokeLinecap="round" strokeLinejoin="round"
                                        strokeWidth="2"
                                        d="M16 12H4m12 0-4 4m4-4-4-4m3-4h2a3 3 0 0 1 3 3v10a3 3 0 0 1-3 3h-2" />
                                </svg>
                                <h1 class="ml-2 block py-2 text-sm">Sign out</h1>
                            </button>
                        </form>
                    </div>
                </div>
            </div>
        </div>
    </div>
    </div>
</nav>
