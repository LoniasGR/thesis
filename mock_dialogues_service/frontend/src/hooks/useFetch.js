import { useState, useEffect } from 'react';

function useFetch(initialUrl, initialOptions, deps) {
  const [url, setUrl] = useState(initialUrl);
  const [options, setOptions] = useState(initialOptions);
  const [data, setData] = useState();
  const [error, setError] = useState();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(undefined);

    function fetchData() {
      fetch(url, options)
        .then((res) => res.json())
        .then((json) => setData(json))
        .catch((e) => { console.error(e); setError(e); })
        .finally(() => setLoading(false));
    }

    fetchData();
  }, [url, options, ...deps]);

  return {
    data, error, loading, setUrl, setOptions,
  };
}

export default useFetch;
