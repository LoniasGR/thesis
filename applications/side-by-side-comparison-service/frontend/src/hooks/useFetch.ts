import { useState, useEffect } from "react";
import axios, { AxiosResponse } from "axios";

export function useAPI(initialUrl: string, deps: any[]) {
  const [url, setUrl] = useState<string>(initialUrl);
  const [data, setData] = useState();
  const [error, setError] = useState<Error>();
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    setLoading(true);
    setError(undefined);

    function fetchData() {
      return axios
        .get(url)
        .then((d: AxiosResponse) => {
          console.log(d);
          setData(d.data);
        })
        .catch((e: Error) => {
          console.error(e);
          setError(e);
        })
        .finally(() => setLoading(false));
    }

    fetchData();
  }, [url, ...deps]);

  return {
    data,
    error,
    loading,
    setUrl,
  };
}
