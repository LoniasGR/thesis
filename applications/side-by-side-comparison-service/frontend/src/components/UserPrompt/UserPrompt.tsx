/* eslint-disable react/jsx-props-no-spreading */
import { useLayoutEffect, useState, useRef, useEffect } from "react";
import Collapse from "@mui/material/Collapse";
import ArrowRightIcon from "@mui/icons-material/ArrowRight";

import "./UserPrompt.css";

interface UserPromptProps {
  description: string;
  response: string;
  demonstrate?: boolean;
  initialExpansion?: boolean;
  className?: string;
}

export function UserPrompt({
  description,
  response,
  demonstrate = false,
  initialExpansion = false,
  className = "",
}: UserPromptProps) {
  const [isExpanded, setIsExpanded] = useState(initialExpansion);
  const collapsible = useRef<HTMLLIElement>(null);

  useEffect(() => {
    if (demonstrate) {
      setTimeout(() => {
        setIsExpanded(true);
        setTimeout(() => {
          setIsExpanded(false);
        }, 2000);
      }, 2000);
    }
  }, [demonstrate]);

  useLayoutEffect(() => {
    let startTouchPosX: number;
    let startTouchPosY: number;
    const elem: HTMLLIElement = collapsible.current!;
    const onClick = (e: MouseEvent) => {
      e.preventDefault();
      e.stopPropagation();
      setIsExpanded(!isExpanded);
    };

    const onTouchEnd = (e: TouchEvent) => {
      e.preventDefault();
      const endTouchPosY = e.changedTouches[0].clientY;
      const endTouchPosX = e.changedTouches[0].clientX;
      const movement =
        Math.abs(endTouchPosX - startTouchPosX) +
        Math.abs(endTouchPosY - startTouchPosY);
      if (movement < 10) {
        setIsExpanded(!isExpanded);
      }
      elem.removeEventListener("touchend", onTouchEnd);
    };

    const onTouchStart = (e: TouchEvent) => {
      e.preventDefault();
      startTouchPosY = e.changedTouches[0].clientY;
      startTouchPosX = e.changedTouches[0].clientX;

      elem.addEventListener("touchend", onTouchEnd);
    };

    elem.addEventListener("click", onClick);
    elem.addEventListener("touchstart", onTouchStart);
    return () => {
      elem.removeEventListener("click", onClick);
      elem.removeEventListener("touchstart", onTouchStart);
    };
  }, [collapsible, isExpanded, setIsExpanded]);

  return (
    <li
      className={`${className} ${isExpanded ? "user user-open" : "user"}`}
      ref={collapsible}
    >
      <div className="clickable">
        {isExpanded ? (
          <ArrowRightIcon className="rotated" />
        ) : (
          <ArrowRightIcon />
        )}
        <div>
          <span className="bold user-question">Ο χρήστης ρώτησε: </span>
          {description}
        </div>
      </div>
      <Collapse in={isExpanded}>
        <div className="reply">
          <span className="bold">Η Θεανώ απάντησε: </span>
          {response}
        </div>
      </Collapse>
    </li>
  );
}
