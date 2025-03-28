import { useState } from 'react'
import reactLogo from './assets/react.svg'
import viteLogo from '/vite.svg'
import './App.css'

function App() {
  const [count, setCount] = useState(0)

  async function logout() {
    const res = await fetch("/users/logout/", {
      method: "POST",
      headers: {
        'Authorization': `Token ${userToken}`,
        'Content-Type': 'application/json',
      },
    });

    if (res.ok) {
      // navigate away from the single page app!
      window.location = "/registration/sign_in/";
    } else {
      // handle logout failed!
    }
  }

  return (
    <>
      
    </>
  )
}

export default App;
